"""Token validation for OAuth2/OIDC access tokens.

Validates JWT tokens using JWKS from the auth server via OIDC Discovery.
"""

import base64
import json
import sys
from typing import Any, Dict, Optional

import httpx
from authlib.jose import jwt
from fastapi import HTTPException, status


class TokenValidator:
    """Validates OAuth2/OIDC access tokens using JWKS."""

    def __init__(self, auth_server_url: str) -> None:
        """Initialize token validator.

        Args:
            auth_server_url: Base URL of the OAuth2/OIDC auth server
        """
        self.auth_server_url: str = auth_server_url.rstrip("/")
        self._jwks_uri: Optional[str] = None
        self._issuer: Optional[str] = None

    async def _load_discovery_document(self) -> Dict[str, Any]:
        """Load OIDC discovery document from auth_server."""
        discovery_url = f"{self.auth_server_url}/.well-known/openid-configuration"
        async with httpx.AsyncClient() as client:
            response = await client.get(discovery_url, timeout=10)
            response.raise_for_status()
            return response.json()

    async def _get_jwks(self) -> Dict[str, Any]:
        """Get JWKS from auth server using discovery.

        Always fetches fresh JWKS to handle key rotation.
        In production, you might want to cache with TTL and handle key rotation gracefully.
        """
        # Always fetch fresh JWKS to avoid stale key issues after server restarts
        # The auth server generates new keys on each restart, so cached JWKS becomes invalid
        discovery = await self._load_discovery_document()
        self._issuer = discovery["issuer"]
        self._jwks_uri = discovery["jwks_uri"]

        # Fetch fresh JWKS
        async with httpx.AsyncClient() as client:
            response = await client.get(self._jwks_uri, timeout=10)
            response.raise_for_status()
            jwks = response.json()

        return jwks

    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate access token and return claims.

        Uses Authlib to decode and validate JWT tokens from auth_server.

        Args:
            token: JWT access token

        Returns:
            Token claims if valid

        Raises:
            HTTPException: If token is invalid
        """
        try:
            # Manually decode JWT header to get kid (jwt is a class, not a module with get_unverified_header)
            # JWT format: header.payload.signature (each part is base64url encoded)
            try:
                parts = token.split(".")
                if len(parts) != 3:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token format: JWT must have 3 parts",
                    )

                # Decode header (add padding if needed for base64)
                header_b64 = parts[0]
                header_b64 += "=" * (4 - len(header_b64) % 4)  # Add padding
                header_json = base64.urlsafe_b64decode(header_b64)
                decoded_header = json.loads(header_json)

                token_kid = decoded_header.get("kid")
                token_alg = decoded_header.get("alg")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Failed to decode token header: {str(e)}",
                )

            # Get JWKS
            jwks = await self._get_jwks()

            # Verify the key exists in JWKS
            matching_key = None
            for key in jwks.get("keys", []):
                if key.get("kid") == token_kid:
                    matching_key = key
                    break

            if not matching_key:
                available_kids = [k.get("kid") for k in jwks.get("keys", [])]
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Key with kid '{token_kid}' not found in JWKS. Available kids: {available_kids}",
                )

            # Authlib's jwt.decode can accept JWKS dict directly
            # It will automatically resolve the key by kid from the token header
            # This is simpler and more reliable than importing key sets
            claims = jwt.decode(
                token,
                jwks,  # Pass JWKS dict directly - Authlib handles kid resolution
                claims_options={
                    "iss": {"essential": True, "value": self._issuer},
                    "exp": {"essential": True},
                },
            )

            # Validate claims (expiration, etc.)
            claims.validate()

            # Authlib's Claims object is dict-like and supports .get() and dict operations
            # Just return it as-is - it should work with claims.get("scope")
            return claims
        except HTTPException:
            # Re-raise HTTPException as-is
            raise
        except Exception as e:
            # More detailed error information for debugging
            import traceback

            error_details = traceback.format_exc()
            # Print to stderr so it shows up in server logs
            print(f"Token validation error details:\n{error_details}", file=sys.stderr)

            # Try to decode without validation to see what's in the token
            try:
                # Manually decode header and payload for debugging
                parts = token.split(".")
                if len(parts) == 3:
                    # Decode header
                    header_b64 = parts[0] + "=" * (4 - len(parts[0]) % 4)
                    header_json = base64.urlsafe_b64decode(header_b64)
                    decoded_header = json.loads(header_json)

                    # Decode payload
                    payload_b64 = parts[1] + "=" * (4 - len(parts[1]) % 4)
                    payload_json = base64.urlsafe_b64decode(payload_b64)
                    decoded_payload = json.loads(payload_json)

                    print(f"Token header: {decoded_header}", file=sys.stderr)
                    print(f"Token payload (iss): {decoded_payload.get('iss')}", file=sys.stderr)
                    print(f"Expected issuer: {self._issuer}", file=sys.stderr)
                    if jwks:
                        print(
                            f"JWKS key IDs: {[k.get('kid') for k in jwks.get('keys', [])]}",
                            file=sys.stderr,
                        )
            except Exception as decode_error:
                print(f"Could not decode token for debugging: {decode_error}", file=sys.stderr)

            # Return more specific error message
            error_msg = str(e)
            if "Key not found" in error_msg or "key" in error_msg.lower():
                if jwks:
                    error_msg = f"Key lookup failed: {error_msg}. Token kid: {token_kid}, Available kids: {[k.get('kid') for k in jwks.get('keys', [])]}"

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid or expired token: {error_msg}",
            )

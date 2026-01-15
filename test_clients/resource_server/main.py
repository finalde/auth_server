"""Resource Server - Protected API.

This is a test resource server that protects its endpoints using OAuth2 access tokens
from the auth_server. It uses Authlib to validate tokens via OIDC Discovery and JWKS.

This demonstrates a Web API using auth_server for authentication and authorization.
"""

import base64
import json
import httpx
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from authlib.jose import JsonWebKey, jwt
from authlib.jose.errors import DecodeError, BadSignatureError

app: FastAPI = FastAPI(
    title="Resource Server API",
    description="Protected resource server using auth_server for OAuth2/OIDC",
    version="1.0.0",
)

security = HTTPBearer()
AUTH_SERVER_URL: str = "http://localhost:8000"

# JWKS URI and issuer (no cache - always fetch fresh to handle key rotation)
# The auth server generates new keys on each restart, so caching JWKS causes stale key errors
_jwks_uri: Optional[str] = None
_issuer: Optional[str] = None


async def _load_discovery_document() -> dict:
    """Load OIDC discovery document from auth_server."""
    discovery_url = f"{AUTH_SERVER_URL}/.well-known/openid-configuration"
    async with httpx.AsyncClient() as client:
        response = await client.get(discovery_url, timeout=10)
        response.raise_for_status()
        return response.json()


async def _get_jwks() -> dict:
    """Get JWKS from auth server using discovery.
    
    Always fetches fresh JWKS to handle key rotation.
    In production, you might want to cache with TTL and handle key rotation gracefully.
    """
    global _jwks_uri, _issuer
    
    # Always fetch fresh JWKS to avoid stale key issues after server restarts
    # The auth server generates new keys on each restart, so cached JWKS becomes invalid
    discovery = await _load_discovery_document()
    _issuer = discovery["issuer"]
    _jwks_uri = discovery["jwks_uri"]
    
    # Fetch fresh JWKS
    async with httpx.AsyncClient() as client:
        response = await client.get(_jwks_uri, timeout=10)
        response.raise_for_status()
        jwks = response.json()
    
    return jwks


def _validate_token(token: str, jwks: dict) -> dict:
    """Validate access token and return claims.

    Uses Authlib to decode and validate JWT tokens from auth_server.
    
    Args:
        token: JWT access token
        jwks: JSON Web Key Set from auth_server
        
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
                    detail="Invalid token format: JWT must have 3 parts"
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
                detail=f"Failed to decode token header: {str(e)}"
            )
        
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
                detail=f"Key with kid '{token_kid}' not found in JWKS. Available kids: {available_kids}"
            )
        
        # Authlib's jwt.decode can accept JWKS dict directly
        # It will automatically resolve the key by kid from the token header
        # This is simpler and more reliable than importing key sets
        claims = jwt.decode(
            token,
            jwks,  # Pass JWKS dict directly - Authlib handles kid resolution
            claims_options={
                "iss": {"essential": True, "value": _issuer},
                "exp": {"essential": True},
            },
        )
        
        # Validate claims (expiration, etc.)
        claims.validate()
        
        print(f"DEBUG: Token validation successful")
        return claims
    except Exception as e:
        # More detailed error information for debugging
        import traceback
        error_details = traceback.format_exc()
        # Print to stderr so it shows up in server logs
        import sys
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
                print(f"Expected issuer: {_issuer}", file=sys.stderr)
                print(f"JWKS key IDs: {[k.get('kid') for k in jwks.get('keys', [])]}", file=sys.stderr)
        except Exception as decode_error:
            print(f"Could not decode token for debugging: {decode_error}", file=sys.stderr)
        
        # Return more specific error message
        error_msg = str(e)
        if "Key not found" in error_msg or "key" in error_msg.lower():
            error_msg = f"Key lookup failed: {error_msg}. Token kid: {token_kid}, Available kids: {[k.get('kid') for k in jwks.get('keys', [])]}"
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {error_msg}"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Dependency to get current authenticated user.

    Validates JWT token from auth_server using Authlib and OIDC Discovery.
    """
    token = credentials.credentials
    
    # Get JWKS (uses discovery for auto-configuration)
    jwks = await _get_jwks()
    
    # Validate token
    claims = _validate_token(token, jwks)
    
    return claims


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - public."""
    return {
        "message": "Resource Server API",
        "status": "public",
        "auth_server": AUTH_SERVER_URL,
        "note": "This server uses auth_server for authentication and authorization"
    }


@app.get("/protected")
async def protected_resource(
    current_user: dict = Depends(get_current_user)
) -> JSONResponse:
    """Protected resource endpoint.

    Requires valid OAuth2 access token from auth_server.
    """
    return JSONResponse(
        content={
            "message": "This is a protected resource",
            "user": {
                "sub": current_user.get("sub"),
                "scopes": current_user.get("scope", "").split() if current_user.get("scope") else [],
            },
            "resource": "data_from_resource_server",
            "authenticated_via": "auth_server",
        }
    )


@app.get("/api/data")
async def get_data(
    current_user: dict = Depends(get_current_user)
) -> JSONResponse:
    """Get protected data.

    Requires valid OAuth2 access token from auth_server.
    """
    return JSONResponse(
        content={
            "data": [
                {"id": 1, "name": "Item 1", "value": 100},
                {"id": 2, "name": "Item 2", "value": 200},
                {"id": 3, "name": "Item 3", "value": 300},
            ],
            "user": current_user.get("sub", "unknown"),
            "authenticated_via": "auth_server",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

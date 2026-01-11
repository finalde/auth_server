"""Resource Server - Protected API.

This is a test resource server that protects its endpoints using OAuth2 access tokens
from the auth_server. It uses Authlib to validate tokens via OIDC Discovery and JWKS.

This demonstrates a Web API using auth_server for authentication and authorization.
"""

import httpx
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from authlib.jose import JsonWebKey, jwt

app: FastAPI = FastAPI(
    title="Resource Server API",
    description="Protected resource server using auth_server for OAuth2/OIDC",
    version="1.0.0",
)

security = HTTPBearer()
AUTH_SERVER_URL: str = "http://localhost:8000"

# Cache for JWKS (in production, refresh periodically)
_jwks_cache: Optional[dict] = None
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
    """Get JWKS from auth server using discovery."""
    global _jwks_cache, _jwks_uri, _issuer
    
    if _jwks_cache is None:
        # Load discovery document
        discovery = await _load_discovery_document()
        _issuer = discovery["issuer"]
        _jwks_uri = discovery["jwks_uri"]
        
        # Fetch JWKS
        async with httpx.AsyncClient() as client:
            response = await client.get(_jwks_uri, timeout=10)
            response.raise_for_status()
            _jwks_cache = response.json()
    
    return _jwks_cache


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
        # Import JWKS
        key_set = JsonWebKey.import_key_set(jwks)
        
        # Decode and validate token
        claims = jwt.decode(
            token,
            key_set,
            claims_options={
                "iss": {"essential": True, "value": _issuer},
                "exp": {"essential": True},
            },
        )
        
        # Validate claims (expiration, etc.)
        claims.validate()
        
        return claims
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}"
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

"""Resource Server - Protected API.

This is a test resource server that protects its endpoints using OAuth2 access tokens
from the auth_server. It uses the authorization library for policy-based authorization.

This demonstrates a Web API using auth_server for authentication and authorization.

Usage:
    # Option 1: Run as module from project root (recommended)
    python -m test_clients.resource_server.main
    
    # Option 2: Install package in editable mode first
    pip install -e .
    python test_clients/resource_server/main.py
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from libs.infrastructure.authorization import Authorize, configure_authorization
from test_clients.resource_server.policies import ReadScopePolicy, WriteScopePolicy

app: FastAPI = FastAPI(
    title="Resource Server API",
    description="Protected resource server using auth_server for OAuth2/OIDC",
    version="1.0.0",
)

AUTH_SERVER_URL: str = "http://localhost:8000"


@app.on_event("startup")
async def startup_event() -> None:
    """Configure authorization library on application startup."""
    configure_authorization(auth_server_url=AUTH_SERVER_URL)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - public."""
    return {
        "message": "Resource Server API",
        "status": "public",
        "auth_server": AUTH_SERVER_URL,
        "note": "This server uses auth_server for authentication and authorization"
    }


@app.get("/public")
async def public_resource() -> JSONResponse:
    """Public resource endpoint - no authentication required."""
    return JSONResponse(
        content={
            "message": "This is a public resource",
            "status": "public",
            "data": "Anyone can access this endpoint"
        }
    )


@app.get("/protected/read")
@Authorize(policy=ReadScopePolicy())
async def protected_read_resource(request: Request) -> JSONResponse:
    """Protected resource endpoint requiring 'read' scope.

    Uses @Authorize decorator with ReadScopePolicy to enforce authorization.
    Requires valid OAuth2 access token with 'read' scope from auth_server.
    
    Note: Token claims may represent:
    - Client (client credentials flow): claims['sub'] = client_id
    - User (authorization code flow): claims['sub'] = user_id
    """
    # Token claims are available in request.state.claims (or request.state.user for compatibility)
    # In client credentials flow, there is no user - the claims represent the client
    # Starlette's State uses attribute access, not dict-style .get() method
    claims = getattr(request.state, 'claims', None) or getattr(request.state, 'user', None)
    if not claims:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Claims not found in request state"
        )
    # Ensure claims is a dict (should always be, but check for safety)
    if not isinstance(claims, dict):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid claims type: {type(claims)}"
        )
    scopes = claims.get("scope", "").split() if claims.get("scope") else []

    return JSONResponse(
        content={
            "message": "This is a protected resource requiring 'read' scope",
            "user": {
                "sub": claims.get("sub"),
                "scopes": scopes,
            },
            "resource": "read_data_from_resource_server",
            "authenticated_via": "auth_server",
        }
    )


@app.get("/protected/write")
@Authorize(policy=WriteScopePolicy())
async def protected_write_resource(request: Request) -> JSONResponse:
    """Protected resource endpoint requiring 'write' or 'admin' scope.

    Uses @Authorize decorator with WriteScopePolicy to enforce authorization.
    Requires valid OAuth2 access token with 'write' or 'admin' scope from auth_server.
    
    Note: Token claims may represent:
    - Client (client credentials flow): claims['sub'] = client_id
    - User (authorization code flow): claims['sub'] = user_id
    """
    # Token claims are available in request.state.claims (or request.state.user for compatibility)
    # In client credentials flow, there is no user - the claims represent the client
    # Starlette's State uses attribute access, not dict-style .get() method
    claims = getattr(request.state, 'claims', None) or getattr(request.state, 'user', None)
    if not claims:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Claims not found in request state"
        )
    # Ensure claims is a dict (should always be, but check for safety)
    if not isinstance(claims, dict):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid claims type: {type(claims)}"
        )
    scopes = claims.get("scope", "").split() if claims.get("scope") else []

    return JSONResponse(
        content={
            "message": "This is a protected resource requiring 'write' or 'admin' scope",
            "user": {
                "sub": claims.get("sub"),
                "scopes": scopes,
            },
            "resource": "write_data_from_resource_server",
            "authenticated_via": "auth_server",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

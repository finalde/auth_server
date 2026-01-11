"""Caller WebAPI - Service-to-Service OAuth2 Client.

This webapi acts as a caller service that uses Authorization Code flow via Authlib
to get tokens and then calls the resource server on behalf of users.

Uses Authlib for OIDC Discovery and token management.
"""

from typing import Optional
import secrets

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
import httpx

app: FastAPI = FastAPI(
    title="Caller WebAPI",
    description="Service that calls resource server using OAuth2 via Authlib",
    version="1.0.0",
)

AUTH_SERVER_URL = "http://localhost:8000"
RESOURCE_SERVER_URL = "http://localhost:8001"
CLIENT_ID = "caller_webapi"
CLIENT_SECRET = "caller_secret"
REDIRECT_URI = "http://localhost:8002/callback"

# Initialize OAuth with Authlib (uses OIDC Discovery)
oauth = OAuth()
oauth.register(
    name="auth_server",
    server_metadata_url=f"{AUTH_SERVER_URL}/.well-known/openid-configuration",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile api:read",
    },
)

# In-memory token storage (use proper storage in production)
token_storage: dict[str, dict] = {}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Caller WebAPI",
        "status": "ready",
        "auth_server": AUTH_SERVER_URL,
        "note": "Uses Authlib for OAuth2/OIDC client functionality"
    }


@app.get("/login")
async def login(request: Request) -> RedirectResponse:
    """Initiate OAuth2 login flow using Authlib.

    Authlib handles OIDC Discovery automatically.
    """
    return await oauth.auth_server.authorize_redirect(request, REDIRECT_URI)


@app.get("/callback")
async def callback(request: Request) -> dict:
    """OAuth2 callback endpoint.

    Authlib handles token exchange and ID token validation.
    """
    try:
        # Exchange code for tokens (Authlib handles this)
        token = await oauth.auth_server.authorize_access_token(request)
        
        # Parse ID token (Authlib validates it automatically)
        user = await oauth.auth_server.parse_id_token(request, token)
        
        # Store token (simplified - use proper session/user storage)
        session_id = getattr(request.state, "session_id", secrets.token_urlsafe(16))
        token_storage[session_id] = {
            "access_token": token["access_token"],
            "id_token": token.get("id_token"),
            "refresh_token": token.get("refresh_token"),
            "user": user,
        }
        
        return {
            "message": "Authentication successful",
            "user": {
                "sub": user.get("sub"),
                "email": user.get("email"),
            },
            "access_token": token["access_token"][:20] + "...",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@app.get("/call-resource")
async def call_resource(request: Request) -> dict:
    """Call protected resource on behalf of user."""
    session_id = getattr(request.state, "session_id", "default")
    
    if session_id not in token_storage:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please visit /login first."
        )
    
    token_data = token_storage[session_id]
    access_token = token_data["access_token"]
    
    try:
        # Call resource server
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{RESOURCE_SERVER_URL}/api/data",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "message": "Resource accessed successfully",
                    "user": token_data["user"],
                    "data": response.json(),
                }
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Resource server error: {response.text}"
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to call resource: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

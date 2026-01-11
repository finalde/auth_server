"""Auth controller for OAuth2/OpenID Connect endpoints."""

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from apps.webapi.routes import API_BASE, AUTH_BASE, AUTH_LOGIN, AUTH_LOGOUT

router: APIRouter = APIRouter(prefix=AUTH_BASE, tags=["auth"])


@router.get("/authorization", response_model=None)
async def authorization_endpoint(
    request: Request,
) -> HTMLResponse | RedirectResponse:
    """Authorization endpoint for OAuth2 authorization code flow."""
    # TODO: Implement IdPyOIDC authorization endpoint
    return HTMLResponse("<html><body>Authorization endpoint - Coming soon</body></html>")


@router.post("/token")
async def token_endpoint(request: Request) -> dict:
    """Token endpoint for OAuth2 token exchange."""
    # TODO: Implement IdPyOIDC token endpoint
    return {"error": "token_endpoint - Coming soon"}


@router.get("/userinfo")
async def userinfo_endpoint(request: Request) -> dict:
    """UserInfo endpoint for OpenID Connect user information."""
    # TODO: Implement IdPyOIDC userinfo endpoint
    return {"error": "userinfo_endpoint - Coming soon"}


@router.get("/.well-known/openid-configuration")
async def openid_configuration(request: Request) -> dict:
    """OpenID Connect discovery endpoint."""
    base_url: str = str(request.base_url).rstrip("/")
    return {
        "issuer": f"{base_url}",
        "authorization_endpoint": f"{base_url}{AUTH_BASE}/authorization",
        "token_endpoint": f"{base_url}{AUTH_BASE}/token",
        "userinfo_endpoint": f"{base_url}{AUTH_BASE}/userinfo",
        "jwks_uri": f"{base_url}{AUTH_BASE}/jwks",
        "response_types_supported": ["code", "token", "id_token"],
        "grant_types_supported": [
            "authorization_code",
            "client_credentials",
            "refresh_token",
        ],
        "scopes_supported": ["openid", "profile", "email"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
    }


@router.get("/jwks")
async def jwks_endpoint(request: Request) -> dict:
    """JSON Web Key Set endpoint."""
    # TODO: Implement JWKS endpoint with actual keys
    return {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "kid": "default",
                "alg": "RS256",
                # TODO: Add actual public key
            }
        ]
    }


@router.get("/login")
async def login_endpoint(request: Request) -> HTMLResponse:
    """Login page endpoint."""
    # TODO: Implement login page
    return HTMLResponse(
        "<html><body><h1>Login</h1><form method='post'><input type='text' name='username'><input type='password' name='password'><button type='submit'>Login</button></form></body></html>"
    )


@router.post("/login")
async def login_submit(request: Request) -> RedirectResponse:
    """Handle login form submission."""
    # TODO: Implement login logic
    return RedirectResponse(url=f"{AUTH_BASE}/authorization", status_code=302)


@router.post("/logout")
async def logout_endpoint(request: Request) -> dict:
    """Logout endpoint."""
    # TODO: Implement logout logic
    return {"message": "Logged out successfully"}


@router.get("/.well-known/oauth-authorization-server")
async def oauth_authorization_server(request: Request) -> dict:
    """OAuth2 Authorization Server Metadata endpoint."""
    base_url: str = str(request.base_url).rstrip("/")
    return {
        "issuer": f"{base_url}",
        "authorization_endpoint": f"{base_url}{AUTH_BASE}/authorization",
        "token_endpoint": f"{base_url}{AUTH_BASE}/token",
        "jwks_uri": f"{base_url}{AUTH_BASE}/jwks",
        "response_types_supported": ["code", "token"],
        "grant_types_supported": [
            "authorization_code",
            "client_credentials",
            "refresh_token",
        ],
        "scopes_supported": ["openid", "profile", "email"],
    }

"""FastAPI application entry point.

This module sets up the FastAPI application and integrates IdPyOIDC server.
For IdPyOIDC integration details, see:
- IdPyOIDC docs: https://idpy-oidc.readthedocs.io/en/latest/server/contents/index.html
- FastAPI integration: See apps/webapi/docs/IDPYOIDC_INTEGRATION.md
"""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from apps.webapi.controllers import auth__controller
from apps.webapi.dependencies import get_config
from apps.webapi.routes import HEALTH, router
from libs.infrastructure.services.oidc_client_database import create_oidc_cdb
from libs.infrastructure.services.oidc_server_service import OIDCServerService

app: FastAPI = FastAPI(
    title="Auth Server API",
    description="OpenID Connect Provider API",
    version="1.0.0",
)

# CORS configuration – read allowed origins from config.yml (no hard-coded URLs)
_config = get_config()
_allowed_origins = _config.get_cors_allow_origins()

app.add_middleware(
    CORSMiddleware,
    # If no origins are configured, CORS is effectively disabled
    allow_origins=_allowed_origins or [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)
# Well-known endpoints must be at root level per OAuth2/OIDC specification
app.include_router(auth__controller.well_known_router)
# Auth endpoints under /api/v1/auth
app.include_router(auth__controller.router)

# Mount static files (if needed)
# app.mount("/static", StaticFiles(directory="apps/webapi/static"), name="static")


class OIDCMiddleware(BaseHTTPMiddleware):
    """Middleware to inject OIDC server into request state.

    This middleware ensures the IdPyOIDC Server instance is available
    in request.state for all endpoints. The server is initialized once
    on startup and reused for all requests.
    """

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Dispatch request with OIDC server in state."""
        # Get or initialize OIDC server service
        if not hasattr(request.app.state, "oidc_server_service"):
            config = get_config()
            host: str = config.get_server_host()
            port: int = config.get_server_port()
            # Use localhost instead of 0.0.0.0 for issuer URL
            # OIDC Discovery requires issuer to be a valid, reachable URL
            if host == "0.0.0.0":
                host = "localhost"
            base_url: str = f"http://{host}:{port}"
            
            # Create CDB (Client Database) for IdPyOIDC
            database_url: str = config.get_database_url()
            cdb = create_oidc_cdb(database_url)
            
            # Configure OIDC server with CDB
            oidc_service = OIDCServerService(issuer=base_url)
            oidc_service.configure({}, cdb=cdb)
            request.app.state.oidc_server_service = oidc_service
        
        request.state.oidc_server = request.app.state.oidc_server_service.get_server()
        response = await call_next(request)
        return response


# Initialize OIDC server on startup
@app.on_event("startup")
async def startup_event() -> None:
    """Initialize OIDC server on startup.

    The IdPyOIDC Server is initialized once at startup and stored in app.state.
    This follows IdPyOIDC patterns where the server is a long-lived singleton.
    """
    config = get_config()
    host: str = config.get_server_host()
    port: int = config.get_server_port()
    # Use localhost instead of 0.0.0.0 for issuer URL
    if host == "0.0.0.0":
        host = "localhost"
    base_url: str = f"http://{host}:{port}"
    
    # Create CDB (Client Database) for IdPyOIDC
    # CDB allows IdPyOIDC to look up clients from our database
    database_url: str = config.get_database_url()
    cdb = create_oidc_cdb(database_url)
    
    # Configure OIDC server with CDB
    oidc_service = OIDCServerService(issuer=base_url)
    oidc_service.configure({}, cdb=cdb)
    app.state.oidc_server_service = oidc_service


app.add_middleware(OIDCMiddleware)


@app.get(HEALTH)
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

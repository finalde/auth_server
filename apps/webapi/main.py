"""FastAPI application entry point."""

from typing import Any

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from apps.webapi.controllers import auth__controller
from apps.webapi.dependencies import get_config
from apps.webapi.routes import HEALTH, router
from libs.infrastructure.services.oidc_server_service import OIDCServerService

app: FastAPI = FastAPI(
    title="Auth Server API",
    description="OpenID Connect Provider API",
    version="1.0.0",
)

# Include routers
app.include_router(router)
# Well-known endpoints must be at root level per OAuth2/OIDC specification
app.include_router(auth__controller.well_known_router)
# Auth endpoints under /api/v1/auth
app.include_router(auth__controller.router)


class OIDCMiddleware(BaseHTTPMiddleware):
    """Middleware to inject OIDC server into request state."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Dispatch request with OIDC server in state."""
        # Get or initialize OIDC server service
        if not hasattr(request.app.state, "oidc_server_service"):
            config = get_config()
            host: str = config.get_server_host()
            port: int = config.get_server_port()
            # Use localhost instead of 0.0.0.0 for issuer URL
            if host == "0.0.0.0":
                host = "localhost"
            base_url: str = f"http://{host}:{port}"
            oidc_service = OIDCServerService(issuer=base_url)
            oidc_service.configure({})
            request.app.state.oidc_server_service = oidc_service
        
        request.state.oidc_server = request.app.state.oidc_server_service.get_server()
        response = await call_next(request)
        return response


# Initialize OIDC server on startup
@app.on_event("startup")
async def startup_event() -> None:
    """Initialize OIDC server on startup."""
    config = get_config()
    host: str = config.get_server_host()
    port: int = config.get_server_port()
    # Use localhost instead of 0.0.0.0 for issuer URL
    if host == "0.0.0.0":
        host = "localhost"
    base_url: str = f"http://{host}:{port}"
    oidc_service = OIDCServerService(issuer=base_url)
    oidc_service.configure({})
    app.state.oidc_server_service = oidc_service


app.add_middleware(OIDCMiddleware)


@app.get(HEALTH)
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

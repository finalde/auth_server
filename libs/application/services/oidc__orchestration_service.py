"""Application service for OIDC orchestration."""

from typing import Any, Dict, Optional

from libs.common.interfaces import ILogger


class OIDCOrchestrationService:
    """Application service for OIDC orchestration."""

    def __init__(self, logger: ILogger) -> None:
        """Initialize OIDC orchestration service."""
        self._logger: ILogger = logger

    def get_oidc_server(self, request: Any) -> Any:
        """Get OIDC server from request state.
        
        The server is injected via middleware (see main.py OIDCMiddleware).
        """
        if not hasattr(request.state, "oidc_server"):
            raise RuntimeError("OIDC server not initialized")
        return request.state.oidc_server

    def build_http_info(self, request: Any) -> Dict[str, Any]:
        """Build http_info dict for IdPyOIDC parse_request.
        
        IdPyOIDC parse_request expects http_info with:
        - headers: Request headers
        - url: Request URL
        - cookies: Request cookies (optional)
        """
        return {
            "headers": dict(request.headers),
            "url": str(request.url),
            "cookies": dict(request.cookies) if hasattr(request, "cookies") else {},
        }

    def get_base_url(self, request: Any) -> str:
        """Get base URL from request, normalizing 0.0.0.0 to localhost.
        
        The issuer URL must match the discovery endpoint origin per OIDC Discovery spec.
        """
        base_url: str = str(request.base_url).rstrip("/")
        # Normalize 0.0.0.0 to localhost for issuer consistency
        if "0.0.0.0" in base_url:
            base_url = base_url.replace("0.0.0.0", "localhost")
        return base_url

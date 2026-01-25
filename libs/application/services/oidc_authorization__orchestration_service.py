"""Application service for OAuth2 authorization endpoint orchestration."""

from typing import Any, Dict, Optional, Set

from libs.common.interfaces import ILogger
from libs.domain.domain_services.scope__domain_service import ScopeDomainService


class IOIDCAuthorizationOrchestrationService:
    """Interface for OAuth2 authorization orchestration service."""

    def process_authorization_request(
        self, request: Any, user: Optional[str]
    ) -> Dict[str, Any]:
        """Process OAuth2 authorization request."""
        pass


class OIDCAuthorizationOrchestrationService(IOIDCAuthorizationOrchestrationService):
    """Application service for OAuth2 authorization endpoint orchestration."""

    def __init__(
        self,
        logger: ILogger,
        oidc_orchestration_service: Any,
        user_scope_query_service: Any,
    ) -> None:
        """Initialize OAuth2 authorization orchestration service."""
        self._logger: ILogger = logger
        self.oidc_service: Any = oidc_orchestration_service  # Public for access
        self._user_scope_service: Any = user_scope_query_service
        self._scope_domain_service = ScopeDomainService()

    def get_client_allowed_scopes(self, server: Any, client_id: Optional[str]) -> Set[str]:
        """Get client-allowed scopes from CDB."""
        if not client_id:
            return set()

        ctx = server.context
        try:
            client_info = ctx.cdb[client_id]
            if isinstance(client_info, dict):
                scopes = client_info.get("scopes", []) or []
            else:
                scopes = getattr(client_info, "scopes", []) or []
            return set(scopes)
        except KeyError:
            return set()

    def _filter_scopes(
        self,
        requested_scopes: Set[str],
        client_id: Optional[str],
        user: Optional[str],
        server: Any,
    ) -> Set[str]:
        """Filter scopes based on client and user permissions."""
        # Get client-allowed scopes
        client_allowed_scopes = self.get_client_allowed_scopes(server, client_id)

        # Get user-allowed scopes
        user_allowed_scopes: Set[str] = set()
        if user:
            user_allowed_scopes = self._user_scope_service.get_user_scopes(user)

        # Use domain service to filter scopes
        return self._scope_domain_service.filter_scopes(
            requested_scopes, client_allowed_scopes, user_allowed_scopes
        )

    def process_authorization_request(
        self, request: Any, user: Optional[str]
    ) -> Dict[str, Any]:
        """Process OAuth2 authorization request."""
        server = self.oidc_service.get_oidc_server(request)
        endpoint = server.endpoint["authorization"]

        # Prepare request data
        request_data = dict(request.query_params)
        if "response_mode" not in request_data:
            request_data["response_mode"] = "query"

        # Apply per-user scope filtering BEFORE calling IdPyOIDC
        client_id = request_data.get("client_id")
        requested_scope_str = request_data.get("scope", "") or ""
        requested_scopes = set(requested_scope_str.split() if requested_scope_str else [])

        # Filter scopes using domain service
        effective_scopes = self._filter_scopes(requested_scopes, client_id, user, server)

        # Update request_data with filtered scopes
        if effective_scopes:
            request_data["scope"] = " ".join(effective_scopes)

        # Debug logging
        self._logger.debug(
            "Authorization endpoint scope filtering",
            extra={
                "user": user,
                "client_id": client_id,
                "requested_scopes": list(requested_scopes),
                "effective_scopes": list(effective_scopes),
            },
        )

        # Build http_info
        http_info = self.oidc_service.build_http_info(request)

        # Parse and process request
        parsed_request = endpoint.parse_request(request_data, http_info=http_info)
        response = endpoint.process_request(parsed_request)

        return {
            "response": response,
            "request_data": request_data,
        }

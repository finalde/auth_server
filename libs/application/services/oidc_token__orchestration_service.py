"""Application service for OAuth2 token endpoint orchestration."""

from typing import Any, Dict

from libs.common.interfaces import ILogger


class OIDCTokenOrchestrationService:
    """Application service for OAuth2 token endpoint orchestration."""

    def __init__(
        self,
        logger: ILogger,
        oidc_orchestration_service: Any,
    ) -> None:
        """Initialize OAuth2 token orchestration service."""
        self._logger: ILogger = logger
        self.oidc_service: Any = oidc_orchestration_service

    async def process_token_request(self, request: Any) -> Dict[str, Any]:
        """Process OAuth2 token request."""
        server = self.oidc_service.get_oidc_server(request)
        endpoint = server.endpoint["token"]

        # Prepare request data
        form_data = await request.form()
        request_data = dict(form_data) if form_data else {}
        http_info = self.oidc_service.build_http_info(request)

        # Debug logging
        client_id = request_data.get("client_id")
        grant_type = request_data.get("grant_type")
        self._logger.debug(
            "Token request",
            extra={"client_id": client_id, "grant_type": grant_type},
        )

        # Parse and process request
        parsed_request = endpoint.parse_request(request_data, http_info=http_info)

        # Check for parse errors
        if isinstance(parsed_request, dict) and "error" in parsed_request:
            return {"error": parsed_request}

        response = endpoint.process_request(parsed_request)

        return {"response": response}

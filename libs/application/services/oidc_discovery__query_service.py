"""Application service for OIDC discovery endpoint orchestration."""

from typing import Any, Dict

from libs.common.interfaces import ILogger


class IOIDCDiscoveryQueryService:
    """Interface for OIDC discovery query service."""

    def get_openid_configuration(self, request: Any) -> Dict[str, Any]:
        """Get OpenID Connect configuration document."""
        pass

    def get_oauth_authorization_server_metadata(self, request: Any) -> Dict[str, Any]:
        """Get OAuth2 Authorization Server Metadata (RFC 8414)."""
        pass


class OIDCDiscoveryQueryService(IOIDCDiscoveryQueryService):
    """Application service for OIDC discovery endpoint orchestration."""

    def __init__(
        self,
        logger: ILogger,
        oidc_orchestration_service: Any,
    ) -> None:
        """Initialize OIDC discovery query service."""
        self._logger: ILogger = logger
        self._oidc_service: Any = oidc_orchestration_service

    def _normalize_provider_info(
        self, provider_info: Dict[str, Any], base_url: str
    ) -> Dict[str, Any]:
        """Normalize provider info to ensure all endpoints use the same base URL."""
        # Set issuer to match the discovery endpoint base URL (MUST rule)
        provider_info["issuer"] = base_url

        # Remove inline jwks if present (should not be in discovery doc)
        if "jwks" in provider_info:
            del provider_info["jwks"]

        # Add required jwks_uri pointing to the JWKS endpoint
        provider_info["jwks_uri"] = f"{base_url}/api/v1/auth/jwks"

        # Ensure ALL endpoints use the same base URL as issuer (MUST rule)
        provider_info["authorization_endpoint"] = f"{base_url}/api/v1/auth/authorization"
        provider_info["token_endpoint"] = f"{base_url}/api/v1/auth/token"
        provider_info["userinfo_endpoint"] = f"{base_url}/api/v1/auth/userinfo"

        # Fix: Ensure registration_endpoint uses same base URL, or remove if not needed
        if "registration_endpoint" in provider_info:
            provider_info["registration_endpoint"] = f"{base_url}/api/v1/auth/registration"

        return provider_info

    def get_openid_configuration(self, request: Any) -> Dict[str, Any]:
        """Get OpenID Connect configuration document."""
        server = self._oidc_service.get_oidc_server(request)
        endpoint_context = server.context
        base_url = self._oidc_service.get_base_url(request)

        # Get provider info from endpoint context
        provider_info: Dict[str, Any] = endpoint_context.provider_info.copy()

        return self._normalize_provider_info(provider_info, base_url)

    def get_oauth_authorization_server_metadata(self, request: Any) -> Dict[str, Any]:
        """Get OAuth2 Authorization Server Metadata (RFC 8414)."""
        server = self._oidc_service.get_oidc_server(request)
        endpoint_context = server.context
        base_url = self._oidc_service.get_base_url(request)

        # Get provider info from endpoint context
        provider_info: Dict[str, Any] = endpoint_context.provider_info.copy()

        return self._normalize_provider_info(provider_info, base_url)

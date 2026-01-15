"""IdPyOIDC server service.

This module implements the IdPyOIDC server service following the official documentation:
https://idpy-oidc.readthedocs.io/en/latest/server/contents/index.html

Configuration structure follows:
https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html
"""

import os
from typing import Any, Dict, Optional

try:
    from idpyoidc.server import Server
    from idpyoidc.server.configure import OPConfiguration
except ImportError:
    # IdPyOIDC not installed - provide stub types
    Server = Any
    OPConfiguration = Any


class OIDCServerService:
    """IdPyOIDC server service.

    Wraps the IdPyOIDC Server class and provides configuration management.
    Follows IdPyOIDC documentation patterns:
    https://idpy-oidc.readthedocs.io/en/latest/server/contents/setup.html
    """

    def __init__(self, issuer: str, base_path: Optional[str] = None) -> None:
        """Initialize OIDC server.

        Args:
            issuer: The issuer URI for the OpenID Provider (OP).
                Must be a unique URI as per OIDC Discovery specification.
            base_path: Base path for configuration files (optional).
        """
        self._issuer: str = issuer
        self._base_path: str = base_path or os.getcwd()
        self._server: Optional[Server] = None
        self._config: Optional[OPConfiguration] = None

    def configure(self, config: Dict[str, Any], cdb: Optional[Any] = None) -> None:
        """Configure OIDC server with custom configuration.

        Configuration structure follows IdPyOIDC documentation:
        https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html

        Args:
            config: Additional configuration dictionary that will be merged
                with default configuration. See IdPyOIDC docs for available options.
            cdb: Optional Client Database (CDB) for client lookups.
                If provided, will be used for client authentication.
                See: https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#client-database-cdb

        Raises:
            RuntimeError: If configuration fails or IdPyOIDC is not installed.
        """
        try:
            # Create key definitions - shared for keys and token handler
            # Key definitions follow IdPyOIDC patterns:
            # https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#keys
            key_defs: list = [
                {"type": "RSA", "use": ["sig"]},
                {"type": "EC", "crv": "P-256", "use": ["sig"]},
            ]
            
            # Build base URL for endpoints (remove trailing slash, normalize 0.0.0.0 to localhost)
            base_url: str = self._issuer.rstrip("/")
            if "0.0.0.0" in base_url:
                base_url = base_url.replace("0.0.0.0", "localhost")
            
            # Configuration structure follows IdPyOIDC documentation:
            # https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html
            config_with_defaults: Dict[str, Any] = {
                "issuer": base_url,
                "httpc_params": {"verify": False},
                # Keys configuration for signing and encryption
                # https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#keys
                "keys": {
                    "key_defs": key_defs,
                },
                # Token handler arguments
                # https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#token-handler-arguments
                # The factory function expects token configurations directly
                "token_handler_args": {
                    "key_defs": key_defs,
                    # Token lifetimes (in seconds)
                    "code": {"lifetime": 600},  # 10 minutes
                    "token": {"lifetime": 3600},  # 1 hour (note: "token" not "access_token")
                    "refresh": {"lifetime": 86400 * 7},  # 7 days
                },
                # Endpoint configuration
                # https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#endpoint
                "endpoint": {
                    "authorization": {
                        "path": "authorization",
                        "class": "idpyoidc.server.oidc.authorization.Authorization",
                        "kwargs": {},
                    },
                    "token": {
                        "path": "token",
                        # Use OAuth2 token endpoint which supports client_credentials
                        # OIDC token endpoint may not support all OAuth2 grant types
                        "class": "idpyoidc.server.oauth2.token.Token",
                        "kwargs": {},
                    },
                    "userinfo": {
                        "path": "userinfo",
                        "class": "idpyoidc.server.oidc.userinfo.UserInfo",
                        "kwargs": {},
                    },
                    "registration": {
                        "path": "registration",
                        "class": "idpyoidc.server.oidc.registration.Registration",
                        "kwargs": {},
                    },
                },
                # Session parameters for session management
                # https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#session-parameters
                "session_params": {
                    "password": os.urandom(16).hex(),
                    "salt": os.urandom(8).hex(),
                },
                # OIDC Discovery configuration (capabilities)
                # https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#capabilities
                "response_types_supported": ["code"],
                "grant_types_supported": ["authorization_code", "client_credentials", "refresh_token"],
                "subject_types_supported": ["public"],
                "scopes_supported": ["openid", "read", "write"],
                "id_token_signing_alg_values_supported": ["RS256"],
                "token_endpoint_auth_methods_supported": [
                    "client_secret_basic",
                    "client_secret_post",
                ],
                **config,
            }
            
            # Don't put CDB in config - it contains unpicklable objects (SQLAlchemy engine)
            # Instead, we'll set it on the server context after initialization
            # Create OPConfiguration following IdPyOIDC setup:
            # https://idpy-oidc.readthedocs.io/en/latest/server/contents/setup.html
            self._config = OPConfiguration(
                conf=config_with_defaults, base_path=self._base_path
            )
            # Initialize Server with configuration
            # Server initialization follows IdPyOIDC patterns:
            # https://idpy-oidc.readthedocs.io/en/latest/server/contents/setup.html
            self._server = Server(self._config)
            
            # Set CDB on server context after initialization (avoids deepcopy issues)
            # IdPyOIDC uses context.cdb for client lookups
            if cdb is not None:
                if hasattr(self._server, 'context'):
                    self._server.context.cdb = cdb
                    print(f"CDB set on server context")
                else:
                    print(f"Warning: Server context not found, CDB may not work")
        except ImportError:
            # IdPyOIDC not installed - server will be None
            self._server = None
        except Exception as e:
            # Re-raise configuration errors for debugging
            raise RuntimeError(f"Failed to configure OIDC server: {e}") from e

    def get_server(self) -> Server:
        """Get configured OIDC server.

        Returns:
            The configured IdPyOIDC Server instance.

        Raises:
            RuntimeError: If server is not configured or IdPyOIDC is not installed.
        """
        if self._server is None:
            raise RuntimeError(
                "OIDC server not configured. Call configure() first or install idpyoidc."
            )
        return self._server

    def get_configuration(self) -> Dict[str, Any]:
        """Get server configuration.

        Returns:
            The configuration dictionary.

        Raises:
            RuntimeError: If server is not configured.
        """
        if self._config is None:
            raise RuntimeError("OIDC server not configured. Call configure() first.")
        return self._config.conf

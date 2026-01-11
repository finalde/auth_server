"""IdPyOIDC server service."""

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
    """IdPyOIDC server service."""

    def __init__(self, issuer: str, base_path: Optional[str] = None) -> None:
        """Initialize OIDC server."""
        self._issuer: str = issuer
        self._base_path: str = base_path or os.getcwd()
        self._server: Optional[Server] = None
        self._config: Optional[OPConfiguration] = None

    def configure(self, config: Dict[str, Any]) -> None:
        """Configure OIDC server with custom configuration."""
        try:
            # Create key definitions - shared for keys and token handler
            key_defs: list = [
                {"type": "RSA", "use": ["sig"]},
                {"type": "EC", "crv": "P-256", "use": ["sig"]},
            ]
            
            config_with_defaults: Dict[str, Any] = {
                "issuer": self._issuer,
                "httpc_params": {"verify": False},
                "keys": {
                    "key_defs": key_defs,
                },
                "token_handler_args": {
                    "key_defs": key_defs,
                },
                "endpoint": {
                    "authorization": {
                        "path": "authorization",
                        "class": "idpyoidc.server.oidc.authorization.Authorization",
                        "kwargs": {},
                    },
                    "token": {
                        "path": "token",
                        "class": "idpyoidc.server.oidc.token.Token",
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
                "session_params": {
                    "password": os.urandom(16).hex(),
                    "salt": os.urandom(8).hex(),
                },
                **config,
            }
            self._config = OPConfiguration(
                conf=config_with_defaults, base_path=self._base_path
            )
            # Server takes configuration object as positional argument
            self._server = Server(self._config)
        except ImportError:
            # IdPyOIDC not installed - server will be None
            self._server = None
        except Exception as e:
            # Re-raise configuration errors for debugging
            raise RuntimeError(f"Failed to configure OIDC server: {e}") from e

    def get_server(self) -> Server:
        """Get configured OIDC server."""
        if self._server is None:
            raise RuntimeError(
                "OIDC server not configured. Call configure() first or install idpyoidc."
            )
        return self._server

    def get_configuration(self) -> Dict[str, Any]:
        """Get server configuration."""
        if self._config is None:
            raise RuntimeError("OIDC server not configured. Call configure() first.")
        return self._config.conf

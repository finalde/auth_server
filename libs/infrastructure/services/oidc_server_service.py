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
                # Configure tokens to use JWT format (required for resource server validation)
                #
                # Important security note:
                # - We do NOT rely on IdPyOIDC's add_claims_by_scope for client_credentials.
                #   That mechanism is OIDC/user-centric and tends to pull userinfo-based claims.
                #   For client_credentials there is no user, only a client, so we:
                #     * keep add_claims_by_scope disabled, and
                #     * add the 'scope' claim explicitly when minting access tokens for
                #       client_credentials in the custom client_credentials helper below.
                # - Access token lifetimes are kept short (15 minutes) for better security.
                "token_handler_args": {
                    "key_defs": key_defs,
                    # Authorization code (opaque token is fine for codes)
                    "code": {"kwargs": {"lifetime": 600}},  # 10 minutes
                    # Access token - use JWT format so resource servers can validate it
                    "token": {
                        "class": "idpyoidc.server.token.jwt_token.JWTToken",
                        "kwargs": {
                            "lifetime": 900,  # 15 minutes
                            # Enable add_claims_by_scope so that access tokens for
                            # authorization_code flows include a 'scope' claim.
                            # For client_credentials, our patched helper already
                            # sets scope explicitly and bypasses userinfo issues.
                            "add_claims_by_scope": True,
                            "alg": "RS256",  # Use RS256 for better compatibility with resource servers
                        },
                    },
                    # Refresh token - use JWT format
                    "refresh": {
                        "class": "idpyoidc.server.token.jwt_token.JWTToken",
                        "kwargs": {
                            "lifetime": 86400 * 7,  # 7 days
                        },
                    },
                    # ID token (always JWT in OIDC)
                    "id_token": {
                        "class": "idpyoidc.server.token.id_token.IDToken",
                        "kwargs": {},
                    },
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
                # UserInfo configuration for claims_interface.get_user_claims
                # IdPyOIDC's Grant.payload_arguments() calls claims_interface.get_user_claims()
                # for authorization_code flows. If "userinfo" is not defined, it raises:
                #   ImproperlyConfigured("userinfo MUST be defined in the configuration")
                # For this demo, we don't maintain a separate userinfo store, so we
                # configure an in-memory UserInfo with an empty DB. This satisfies the
                # configuration requirement and simply returns no user claims.
                #
                # Docs: https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#userinfo
                "userinfo": {
                    "class": "idpyoidc.server.user_info.UserInfo",
                    "kwargs": {
                        "db": {},  # No user claims for now – tokens still include 'scope'
                    },
                },
                # User authentication methods configuration
                # https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#user-authentication
                # This configures the authn_broker with available authentication methods
                # For Authorization Code flow, we need at least one authentication method
                # IdPyOIDC expects "authentication" key (not "user_authn") with methods dict
                "authentication": {
                    "user": {
                        "acr": "urn:mace:incommon:iap:silver",
                        "class": "idpyoidc.server.user_authn.user.NoAuthn",
                        "kwargs": {
                            "user": "diana",  # Default user - will be replaced by actual user from request
                        },
                    },
                },
                # OIDC Discovery configuration (capabilities)
                # https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#capabilities
                "response_types_supported": ["code"],
                "grant_types_supported": ["authorization_code", "client_credentials", "refresh_token"],
                "subject_types_supported": ["public"],
                "scopes_supported": ["openid", "data.read", "data.write", "read", "write", "admin"],  # Include both resource-oriented and legacy scopes
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
            
            # Patch client_credentials helper to work around IdPyOIDC limitations.
            #
            # Why this exists (architectural note):
            # - IdPyOIDC was designed OIDC-first and assumes a user-centric flow.
            # - The built-in client_credentials helper:
            #     * sometimes receives ClientSessionInfo instead of a plain dict from
            #       session_manager.get_session_info, which breaks its assumptions.
            #     * expects userinfo/user claims machinery to be configured, which is
            #       not appropriate for client_credentials (no human user).
            # - Rather than re-implementing token minting in the FastAPI controller,
            #   we patch the helper here so:
            #     * all protocol logic stays inside IdPyOIDC,
            #     * the FastAPI layer can remain a thin HTTP adapter.
            #
            # This patch is intentionally isolated here so that:
            # - It is easy to audit and replace later with:
            #     * a custom Token class, or
            #     * a custom Grant / session manager integration.
            # - The rest of the application does not depend on IdPyOIDC internals.
            #
            # NOTE: This is acceptable for this demo/PoC, but SHOULD be refactored
            #       for a production deployment as described above.
            try:
                from idpyoidc.server.oauth2.token_helper.client_credentials import ClientCredentials
                original_process_request = ClientCredentials.process_request
                
                def patched_process_request(self, request, **kwargs):
                    """Patched process_request that handles ClientSessionInfo correctly."""
                    _context = self.endpoint.upstream_get("context")
                    _mngr = _context.session_manager
                    client_id = request.get("client_id")
                    
                    # Validate client_id before using it
                    # If client_id is None or empty, authentication already failed
                    # Return proper error response instead of letting original code crash
                    if not client_id:
                        # Return proper OAuth2 error response for missing/invalid client_id
                        return self.error_cls(
                            error="invalid_client",
                            error_description="Client authentication failed: missing or invalid client_id"
                        )
                    
                    # Is there a previous session ?
                    try:
                        _session_info = _mngr.get(["client_credentials", client_id])
                        # _mngr.get returns a ClientSessionInfo object, not a dict
                        # We need to get the grant from it
                        if hasattr(_session_info, 'subordinate') and _session_info.subordinate:
                            _grant = _session_info.subordinate[0]
                            # Get branch_id from the grant's session_id or create a new one
                            branch_id = getattr(_grant, 'session_id', None)
                            if not branch_id:
                                # Recreate grant to get branch_id (this will reuse existing grant if present)
                                branch_id = _mngr.add_grant(["client_credentials", client_id])
                                # Get the grant from the new branch_id
                                _session_info_dict = _mngr.get_session_info(branch_id, grant=True)
                                _grant = _session_info_dict.get("grant")
                            else:
                                _session_info_dict = {
                                    "branch_id": branch_id,
                                    "client": _session_info,
                                    "grant": _grant,
                                    "client_id": client_id,
                                }
                        else:
                            # No subordinate grants, create a new one
                            branch_id = _mngr.add_grant(["client_credentials", client_id])
                            _session_info_dict = _mngr.get_session_info(branch_id, grant=True)
                            _grant = _session_info_dict.get("grant")
                    except KeyError:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.debug("No previous session")
                        branch_id = _mngr.add_grant(["client_credentials", client_id])
                        _session_info_dict = _mngr.get_session_info(branch_id, grant=True)
                        # Ensure _session_info is a dict
                        if not isinstance(_session_info_dict, dict):
                            # Convert ClientSessionInfo to dict if needed
                            _session_info_dict = {
                                "branch_id": branch_id,
                                "client": _session_info_dict,
                                "grant": _session_info_dict.subordinate[0] if hasattr(_session_info_dict, 'subordinate') and _session_info_dict.subordinate else None,
                                "client_id": client_id,
                            }
                        _grant = _session_info_dict.get("grant")
                    
                    if not _grant:
                        return self.error_cls(error="server_error", error_description="Failed to get grant")
                    
                    # For client credentials flow, the client IS the user (no human user)
                    # Set grant's sub to client_id (this is what the token's sub claim will be)
                    # This ensures IdPyOIDC knows the subject when minting the token
                    # Try multiple ways to set sub, depending on grant implementation
                    if hasattr(_grant, 'sub'):
                        _grant.sub = client_id
                    if hasattr(_grant, 'set'):
                        try:
                            _grant.set("sub", client_id)
                        except (TypeError, AttributeError):
                            pass  # set() may not be callable or may not accept this signature
                    
                    token_type = "Bearer"
                    
                    # Get client's allowed scopes from CDB
                    # CDB returns 'scopes' not 'allowed_scopes'
                    client_info = _context.cdb[client_id]
                    client_allowed_scopes = client_info.get("scopes", []) if isinstance(client_info, dict) else getattr(client_info, "scopes", [])
                    
                    # Get requested scope from token request (if provided)
                    # IdPyOIDC may return scope as either a string (space-separated) or a list
                    # Filter requested scopes to only include what the client is allowed to have
                    requested_scope_param = request.get("scope", "")
                    if isinstance(requested_scope_param, list):
                        requested_scopes = requested_scope_param
                    elif isinstance(requested_scope_param, str):
                        requested_scopes = requested_scope_param.split() if requested_scope_param else []
                    else:
                        requested_scopes = []
                    
                    # Intersect requested scopes with client's allowed scopes
                    # This ensures we only issue tokens with scopes the client is allowed to have
                    final_scopes = [s for s in requested_scopes if s in client_allowed_scopes]
                    
                    # If no scope was requested, use all allowed scopes (default behavior)
                    # If scope was requested but filtered out, use what remains (or empty if none valid)
                    scope_to_issue = final_scopes if requested_scopes else client_allowed_scopes
                    
                    # Ensure the grant's scope is set (for token handler's add_claims_by_scope)
                    # This is needed because the token handler uses grant.scope to add scope claim
                    if hasattr(_grant, 'scope'):
                        _grant.scope = scope_to_issue
                    elif hasattr(_grant, 'set'):
                        try:
                            _grant.set("scope", scope_to_issue)
                        except (TypeError, AttributeError):
                            pass
                    
                    # Patch grant's payload_arguments to skip user claims for client credentials
                    # IdPyOIDC's grant.mint_token() calls payload_arguments() which calls get_user_claims()
                    # For client credentials, there's no user, so we need to bypass this
                    # The error "userinfo MUST be defined" happens because IdPyOIDC tries to get user claims
                    # even though there's no user in client credentials flow
                    # We need to capture scope_to_issue in the closure so patched_payload_arguments can use it
                    original_payload_arguments = _grant.payload_arguments
                    
                    def patched_payload_arguments(*args, **kwargs):
                        """Patched payload_arguments that skips user claims for client credentials."""
                        try:
                            return original_payload_arguments(*args, **kwargs)
                        except Exception as e:
                            # If it's the userinfo configuration error, bypass it for client credentials
                            # This happens because client credentials has no user, so userinfo claims aren't applicable
                            # The original payload_arguments tries to call get_user_claims() which fails for client credentials
                            error_str = str(e)
                            if "userinfo MUST be defined" in error_str or "ImproperlyConfigured" in error_str:
                                # For client credentials, we need to build payload without user claims
                                # Include scope in the payload to ensure it's in the token
                                # Convert scope list to space-separated string as per JWT scope claim format
                                scope_str = " ".join(scope_to_issue) if isinstance(scope_to_issue, list) else scope_to_issue
                                return {
                                    "sub": client_id,
                                    "scope": scope_str,  # Explicitly include scope in payload
                                }
                            # Re-raise any other exceptions
                            raise
                    
                    _grant.payload_arguments = patched_payload_arguments
                    
                    access_token = self._mint_token(
                        token_class="access_token",
                        grant=_grant,
                        session_id=_session_info_dict.get("branch_id", branch_id),
                        client_id=client_id,
                        based_on=None,
                        scope=scope_to_issue,  # Use filtered scope list - this should add scope claim via add_claims_by_scope
                        token_type=token_type,
                    )
                    
                    _resp = {
                        "access_token": access_token.value,
                        "token_type": token_type,
                        "expires_in": access_token.expires_at - access_token.issued_at,
                    }
                    
                    return _resp
                
                # Apply the patch
                ClientCredentials.process_request = patched_process_request
                print("Patched ClientCredentials.process_request to handle ClientSessionInfo")
            except Exception as e:
                print(f"Warning: Could not patch ClientCredentials: {e}")
                import traceback
                traceback.print_exc()
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

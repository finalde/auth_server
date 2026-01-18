"""Authorize decorator for FastAPI endpoints.

Provides @Authorize decorator with policy-based authorization for OAuth2/OIDC access tokens.

OAuth2 Flow Overview:
---------------------
OAuth2 defines several grant types (flows) for different use cases:

1. **Client Credentials Flow** (client-to-server, no user):
   - Used for machine-to-machine (M2M) authentication
   - Client authenticates with client_id/client_secret
   - Token represents the CLIENT's authorization, not a user's
   - Token claims contain:
     - `sub`: client_id (the client is the subject)
     - `scope`: scopes granted to the client
     - `iss`, `exp`, etc.
   - Example: API service calling another API service

2. **Authorization Code Flow** (user delegation):
   - User authorizes the client application
   - User logs in and grants permissions to the client
   - Token represents the USER's authorization delegated to the client
   - Token claims contain:
     - `sub`: user identifier (user is the subject)
     - `scope`: scopes granted to the user (which client can use)
     - User profile claims (if using OIDC)
   - Example: Web app accessing user's resources on their behalf

3. **Resource Owner Password Credentials** (deprecated):
   - User provides username/password directly to client
   - `sub`: user identifier
   - Not recommended for security reasons

Token Claims Storage:
---------------------
The validated token claims are stored in `request.state.claims` (not `request.state.user`)
to accurately reflect that in client credentials flow, there is no "user" - only a client.

However, for backward compatibility and common usage patterns, we also provide
`request.state.user` which contains the same claims dictionary. The endpoint can
access either:
- `request.state.claims` - Explicitly indicates these are token claims
- `request.state.user` - Common naming convention (may be client or user)

Usage:
------
    # Configure once during application startup:
    from libs.infrastructure.authorization import configure_authorization
    
    configure_authorization(auth_server_url="http://localhost:8000")
    
    # Then use in endpoints:
    @app.get("/protected")
    @Authorize(policy=ReadScopePolicy())
    async def protected_endpoint(request: Request):
        # Access claims - works for both client credentials and user flows
        claims = request.state.claims  # or request.state.user (same data)
        client_or_user_id = claims.get('sub')  # client_id or user_id depending on flow
        scopes = claims.get('scope', '').split()
        return {"message": "access granted"}
"""

import functools
from typing import Any, Callable, Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from libs.infrastructure.authorization.policy import Policy
from libs.infrastructure.authorization.token_validator import TokenValidator


class AuthorizationConfig:
    """Global configuration for authorization library."""

    def __init__(self) -> None:
        """Initialize authorization configuration."""
        self._auth_server_url: Optional[str] = None
        self._security: Optional[HTTPBearer] = None

    def configure(
        self,
        auth_server_url: str,
        security: Optional[HTTPBearer] = None,
    ) -> None:
        """Configure authorization library.

        Args:
            auth_server_url: Base URL of the OAuth2/OIDC auth server
            security: Optional HTTPBearer instance (creates default if not provided)
        """
        self._auth_server_url = auth_server_url
        self._security = security or HTTPBearer()

    def get_auth_server_url(self) -> str:
        """Get configured auth server URL.

        Returns:
            Auth server URL

        Raises:
            RuntimeError: If authorization is not configured
        """
        if self._auth_server_url is None:
            raise RuntimeError(
                "Authorization not configured. Call configure_authorization() during application startup."
            )
        return self._auth_server_url

    def get_security(self) -> HTTPBearer:
        """Get configured security instance.

        Returns:
            HTTPBearer instance

        Raises:
            RuntimeError: If authorization is not configured
        """
        if self._security is None:
            raise RuntimeError(
                "Authorization not configured. Call configure_authorization() during application startup."
            )
        return self._security


# Global configuration instance
_config = AuthorizationConfig()


def configure_authorization(
    auth_server_url: str,
    security: Optional[HTTPBearer] = None,
) -> None:
    """Configure authorization library globally.

    This should be called once during application startup.

    Usage:
        from libs.infrastructure.authorization import configure_authorization
        
        @app.on_event("startup")
        async def startup():
            configure_authorization(auth_server_url="http://localhost:8000")

    Args:
        auth_server_url: Base URL of the OAuth2/OIDC auth server
        security: Optional HTTPBearer instance (creates default if not provided)
    """
    _config.configure(auth_server_url=auth_server_url, security=security)


def require_policy(
    policy: Policy,
    auth_server_url: Optional[str] = None,
    security: Optional[HTTPBearer] = None,
) -> Callable[..., Any]:
    """Create a FastAPI dependency that enforces a policy.

    This function returns a dependency that can be used with FastAPI's Depends().
    This is the recommended approach for maximum flexibility.

    Usage:
        @app.get("/protected")
        async def protected_endpoint(
            request: Request,
            claims: dict = Depends(require_policy(ReadScopePolicy()))
        ):
            return {"message": "access granted", "user": request.state.user}

    Args:
        policy: Policy instance to evaluate
        auth_server_url: Optional auth server URL (uses configured value if not provided)
        security: Optional HTTPBearer instance (uses configured value if not provided)

    Returns:
        FastAPI dependency function
    """
    # Use provided values or fall back to configured values
    server_url = auth_server_url or _config.get_auth_server_url()
    bearer = security or _config.get_security()

    token_validator = TokenValidator(server_url)

    async def policy_dependency(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(bearer),
    ) -> Dict[str, Any]:
        """FastAPI dependency that handles authorization.
        
        Validates the OAuth2 access token and evaluates the policy.
        The token may represent:
        - A client (client credentials flow): claims['sub'] = client_id
        - A user (authorization code flow): claims['sub'] = user_id
        """
        # Extract token from Authorization header
        token = credentials.credentials

        # Validate token (signature, expiry, issuer, etc.)
        # Returns token claims (JWT payload)
        claims = await token_validator.validate_token(token)

        # Evaluate policy with validated claims
        # Policy checks scopes/permissions based on the grant type (client or user)
        policy_result = policy.evaluate(claims, request=request)

        if not policy_result:
            # Policy evaluation failed - client/user doesn't have required permissions
            reason = policy_result.reason or "Access denied by policy"
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=reason,
            )

        # Attach token claims to request state
        # Store as 'claims' to accurately reflect token claims (client or user)
        # Also store as 'user' for backward compatibility (common naming, even for clients)
        # Starlette's State uses attribute assignment, not dict-style assignment
        request.state.claims = claims
        request.state.user = claims  # For backward compatibility

        return claims

    return policy_dependency


class Authorize:
    """Decorator for policy-based authorization on FastAPI endpoints.

    This decorator wraps the endpoint to automatically inject authorization logic.
    It works by creating a dependency and ensuring it's executed before the endpoint.

    Usage:
        # Configure once during startup:
        configure_authorization(auth_server_url="http://localhost:8000")
        
        # Then use in endpoints:
        @app.get("/protected")
        @Authorize(policy=ReadScopePolicy())
        async def protected_endpoint(request: Request):
            # request.state.user contains validated claims
            return {"message": "access granted"}

    Note: For more control, use require_policy() with Depends() instead.

    The decorator:
    1. Validates the OAuth2 access token from the Authorization header
    2. Extracts token claims
    3. Evaluates the policy with the claims
    4. Raises 403 if policy evaluation fails
    5. Attaches validated claims to request.state.user for use in the endpoint
    """

    def __init__(
        self,
        policy: Policy,
        auth_server_url: Optional[str] = None,
        security: Optional[HTTPBearer] = None,
    ) -> None:
        """Initialize Authorize decorator.

        Args:
            policy: Policy instance to evaluate for authorization
            auth_server_url: Optional auth server URL (uses configured value if not provided)
            security: Optional HTTPBearer instance (uses configured value if not provided)
        """
        self.policy: Policy = policy
        self.auth_server_url: Optional[str] = auth_server_url
        self.security: Optional[HTTPBearer] = security

    def __call__(self, endpoint: Callable[..., Any]) -> Callable[..., Any]:
        """Apply authorization to the endpoint.

        Wraps the endpoint to inject authorization dependency logic.
        The authorization is enforced by adding a dependency parameter that FastAPI
        will automatically resolve.

        Args:
            endpoint: FastAPI endpoint function to protect

        Returns:
            Wrapped endpoint function with authorization dependency
        """
        # Store policy and config for lazy evaluation (config might not be set yet at import time)
        policy = self.policy
        auth_server_url = self.auth_server_url
        security = self.security

        # Create dependency function that will be called at runtime
        # This defers config lookup until runtime, not import time
        # First create a simple dependency for credentials extraction
        bearer_for_dep = security or HTTPBearer()  # Temporary, will use configured one at runtime
        
        async def lazy_policy_dependency(
            request: Request,
            credentials: HTTPAuthorizationCredentials = Depends(bearer_for_dep),
        ) -> Dict[str, Any]:
            """Lazy policy dependency that validates token and evaluates policy at runtime.
            
            This is called lazily (at request time) to avoid accessing configuration
            before it's set during application startup.
            
            The validated token claims represent either:
            - Client credentials flow: claims['sub'] = client_id (client is the subject)
            - Authorization code flow: claims['sub'] = user_id (user is the subject)
            """
            # Get config values lazily (only when actually called, not at import time)
            # This allows configure_authorization() to be called during startup event
            server_url = auth_server_url or _config.get_auth_server_url()
            bearer = security or _config.get_security()
            
            # Create token validator and validate token
            # Token validation checks: signature, expiry, issuer, audience, etc.
            token_validator = TokenValidator(server_url)
            token = credentials.credentials
            claims = await token_validator.validate_token(token)
            
            # Debug: Check what's in the claims (temporary for troubleshooting)
            # Convert Claims to dict for inspection if needed
            claims_dict = dict(claims) if hasattr(claims, 'keys') else claims
            if isinstance(claims_dict, dict) and 'scope' not in claims_dict:
                # Token doesn't have scope claim - this is likely the issue
                # IdPyOIDC should include scope in JWT tokens
                import sys
                print(f"WARNING: Token missing 'scope' claim. Available claims: {list(claims_dict.keys())}", file=sys.stderr)
            
            # Evaluate policy with validated claims
            # Policy checks if the authenticated entity (client or user) has required permissions
            policy_result = policy.evaluate(claims, request=request)
            
            if not policy_result:
                # Policy evaluation failed - authenticated entity lacks required permissions
                reason = policy_result.reason or "Access denied by policy"
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=reason,
                )
            
            # Attach token claims to request state for use in endpoint handlers
            # Store as 'claims' to accurately reflect that this contains token claims
            # which may represent a client (client credentials) or user (authorization code)
            # Starlette's State uses attribute assignment, not dict-style assignment
            request.state.claims = claims
            # Also store as 'user' for backward compatibility and common naming convention
            # Note: In client credentials flow, 'user' is misleading but common in APIs
            request.state.user = claims
            
            return claims

        # Wrap the endpoint to inject the authorization dependency
        # FastAPI dependency injection may not work correctly with wrapped functions,
        # so we manually extract credentials and call the dependency logic
        @functools.wraps(endpoint)
        async def wrapped_endpoint(
            request: Request,
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            """Wrapped endpoint with authorization injected.

            The authorization dependency (lazy_policy_dependency) is called manually
            to ensure it runs before the endpoint logic. This ensures request.state.claims
            and request.state.user are set properly.
            """
            # Get the configured security scheme (HTTPBearer) to extract token
            server_url = auth_server_url or _config.get_auth_server_url()
            bearer_scheme = security or _config.get_security() or HTTPBearer()
            
            # Extract credentials from Authorization header using HTTPBearer
            # This mimics what Depends(bearer_for_dep) does in lazy_policy_dependency
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            token = authorization.replace("Bearer ", "")
            
            # Create a mock credentials object for the dependency
            # We need this because lazy_policy_dependency expects HTTPAuthorizationCredentials
            class MockCredentials:
                def __init__(self, token: str):
                    self.credentials = token
            
            credentials = MockCredentials(token)
            
            # Call the dependency function directly with the credentials
            # This sets request.state.claims and request.state.user
            await lazy_policy_dependency(request, credentials=credentials)
            
            # The dependency already set request.state.claims/user and validated everything
            # Just call the original endpoint
            return await endpoint(request, *args, **kwargs)

        return wrapped_endpoint

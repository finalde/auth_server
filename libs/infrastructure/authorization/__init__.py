"""Authorization library for resource servers.

Provides policy-based authorization decorators for FastAPI endpoints.

Usage:
    # Configure once during application startup:
    from libs.infrastructure.authorization import configure_authorization
    
    @app.on_event("startup")
    async def startup():
        configure_authorization(auth_server_url="http://localhost:8000")
    
    # Then use in endpoints:
    from libs.infrastructure.authorization import Authorize
    from my_policies import ReadScopePolicy
    
    @app.get("/protected")
    @Authorize(policy=ReadScopePolicy())
    async def protected_endpoint(request: Request):
        return {"message": "access granted"}
"""

from libs.infrastructure.authorization.authorize import Authorize, configure_authorization, require_policy
from libs.infrastructure.authorization.policy import Policy, PolicyResult

__all__ = ["Authorize", "Policy", "PolicyResult", "configure_authorization", "require_policy"]

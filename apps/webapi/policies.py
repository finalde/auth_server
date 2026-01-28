"""Authorization policies for WebAPI endpoints.

Policies define authorization logic based on token claims and scopes.
"""

from libs.infrastructure.authorization.policy import Policy, PolicyResult


class AdminScopePolicy(Policy):
    """Policy that requires 'admin' scope.

    This policy enforces admin-only access to CRUD operations.
    Only users with the 'admin' scope in their token can access protected endpoints.
    """

    def evaluate(self, claims: dict, **context: dict) -> PolicyResult:
        """Evaluate if the user has 'admin' scope.

        Args:
            claims: Validated JWT claims containing scope and other claims
            **context: Additional context (request, etc.)

        Returns:
            PolicyResult indicating if access is allowed
        """
        scopes = claims.get("scope", "").split() if claims.get("scope") else []
        if "admin" in scopes:
            return PolicyResult(allowed=True)
        return PolicyResult(
            allowed=False,
            reason="Insufficient permissions: 'admin' scope required",
        )

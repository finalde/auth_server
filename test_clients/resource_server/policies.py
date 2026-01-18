"""Authorization policies for the resource server.

Each policy defines authorization logic based on token claims and scopes.

OAuth2 Best Practice: Scope + Claims Authorization Model
---------------------------------------------------------
- Scopes = permission to act (what can the client do?)
- Claims = constraints (under what conditions?)

Authorization Decision = Scope AND Claims
- Scope grants permission (e.g., "data.read" allows calling read API)
- Claims restrict permission (e.g., "trust_level" must be "internal" for write)

This follows OAuth2/RFC 6749 best practices:
- Never use claims alone as permissions (scopes are mandatory)
- Use resource-oriented scopes (data.read, data.write)
- Use claims for fine-grained constraints (tenant_id, trust_level, regions)
"""

from libs.infrastructure.authorization.policy import Policy, PolicyResult


class ReadScopePolicy(Policy):
    """Policy that requires 'data.read' scope.

    Authorization Model:
    - Scope: Must have "data.read" (grants permission to call read API)
    - Claims: Optional constraints (e.g., tenant_id for multi-tenancy)

    This policy enforces:
    ALLOW if:
      - scope contains "data.read"
      - (Optional) claims satisfy additional constraints (checked in policy)
    """

    def evaluate(self, claims: dict, **context: dict) -> PolicyResult:
        """Evaluate if the client has 'data.read' scope.

        Args:
            claims: Validated JWT claims containing scope and other claims
            **context: Additional context (request, etc.)

        Returns:
            PolicyResult indicating if access is allowed
        """
        # Extract scopes from token (scope is space-separated string per RFC 6749)
        scopes = claims.get("scope", "").split() if claims.get("scope") else []
        
        # Check scope: Must have "data.read" (permission to act)
        if "data.read" not in scopes:
            return PolicyResult(
                allowed=False,
                reason="Insufficient permissions: 'data.read' scope required",
            )
        
        # Scope check passed - permission granted
        # Additional claim-based constraints can be added here if needed
        # Example: Check tenant_id, env, etc.
        
        return PolicyResult(allowed=True)


class WriteScopePolicy(Policy):
    """Policy that requires 'data.write' scope AND trust_level claim.

    Authorization Model:
    - Scope: Must have "data.write" (grants permission to call write API)
    - Claims: Must have trust_level == "internal" (constraint on how/who can write)

    This policy enforces:
    ALLOW if:
      - scope contains "data.write"
      - trust_level claim == "internal"
    
    This demonstrates scope + claims authorization:
    - Scope opens the door (grants permission)
    - Claims restrict how far you can walk (enforces constraints)
    """

    def evaluate(self, claims: dict, **context: dict) -> PolicyResult:
        """Evaluate if the client has 'data.write' scope and required claims.

        Args:
            claims: Validated JWT claims containing scope and other claims
            **context: Additional context (request, etc.)

        Returns:
            PolicyResult indicating if access is allowed
        """
        # Extract scopes from token (scope is space-separated string per RFC 6749)
        scopes = claims.get("scope", "").split() if claims.get("scope") else []
        
        # Check scope: Must have "data.write" (permission to act)
        if "data.write" not in scopes:
            return PolicyResult(
                allowed=False,
                reason="Insufficient permissions: 'data.write' scope required",
            )
        
        # Check claims: Must have trust_level == "internal" (constraint)
        # Claims restrict the scope - even with data.write scope, only internal clients can write
        trust_level = claims.get("trust_level") or claims.get("metadata", {}).get("trust_level")
        if trust_level != "internal":
            return PolicyResult(
                allowed=False,
                reason="Insufficient permissions: write requires trust_level='internal' claim",
            )
        
        # Both scope and claims check passed
        return PolicyResult(allowed=True)


class AdminScopePolicy(Policy):
    """Policy that requires 'admin' scope."""

    def evaluate(self, claims: dict, **context: dict) -> PolicyResult:
        """Evaluate if the user has 'admin' scope.

        Args:
            claims: Validated JWT claims
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

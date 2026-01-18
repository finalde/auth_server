"""Policy base class for authorization.

Policies define authorization logic based on token claims, scopes, and other context.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class PolicyResult:
    """Result of policy evaluation."""

    def __init__(self, allowed: bool, reason: Optional[str] = None) -> None:
        """Initialize policy result.

        Args:
            allowed: True if access is allowed, False otherwise
            reason: Optional reason for denial (required if allowed=False)
        """
        self.allowed: bool = allowed
        self.reason: Optional[str] = reason

    def __bool__(self) -> bool:
        """Allow using PolicyResult in boolean context."""
        return self.allowed


class Policy(ABC):
    """Base class for authorization policies.

    Each resource server can define its own policies by extending this class.
    Policies receive the validated token claims and can make authorization decisions
    based on scopes, claims, or custom logic.

    Example:
        class ReadScopePolicy(Policy):
            def evaluate(self, claims: dict, **context: Any) -> PolicyResult:
                scopes = claims.get("scope", "").split() if claims.get("scope") else []
                if "read" in scopes:
                    return PolicyResult(allowed=True)
                return PolicyResult(allowed=False, reason="'read' scope required")
    """

    @abstractmethod
    def evaluate(self, claims: Dict[str, Any], **context: Any) -> PolicyResult:
        """Evaluate the policy against token claims.

        Args:
            claims: Validated JWT claims from the access token
            **context: Additional context (request, endpoint, etc.) that can be used
                for policy evaluation

        Returns:
            PolicyResult indicating whether access is allowed
        """
        pass


"""Domain service for scope-related business logic."""

from typing import Set


class ScopeDomainService:
    """Domain service for scope business logic."""

    @staticmethod
    def filter_scopes(
        requested_scopes: Set[str],
        client_allowed_scopes: Set[str],
        user_allowed_scopes: Set[str],
    ) -> Set[str]:
        """Filter scopes based on client and user permissions.
        
        Business rule: A scope is allowed if:
        1. It's in the requested scopes
        2. It's allowed by the client (or client has no restrictions)
        3. It's allowed by the user (or user has no restrictions)
        4. 'openid' is always allowed if requested and client allows it
        
        Args:
            requested_scopes: Scopes requested by the client
            client_allowed_scopes: Scopes allowed by the client configuration
            user_allowed_scopes: Scopes allowed for the user
            
        Returns:
            Filtered set of allowed scopes
        """
        always_allowed: Set[str] = {"openid"}
        effective_scopes: Set[str] = set()
        
        for scope in requested_scopes:
            # Always allow 'openid' if requested and client allows it
            if scope in always_allowed:
                if not client_allowed_scopes or scope in client_allowed_scopes:
                    effective_scopes.add(scope)
            else:
                # Check client restrictions
                if client_allowed_scopes and scope not in client_allowed_scopes:
                    continue
                # Check user restrictions
                if user_allowed_scopes and scope not in user_allowed_scopes:
                    continue
                effective_scopes.add(scope)
        
        return effective_scopes

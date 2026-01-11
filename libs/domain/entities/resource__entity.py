"""Resource/API entity."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Resource:
    """Resource/API domain entity."""

    resource_id: str
    resource_name: str
    resource_uri: str
    scopes: List[str] = field(default_factory=list)
    description: str = ""
    is_active: bool = True

    def add_scope(self, scope: str) -> None:
        """Add scope to resource."""
        if scope not in self.scopes:
            self.scopes.append(scope)

    def remove_scope(self, scope: str) -> None:
        """Remove scope from resource."""
        if scope in self.scopes:
            self.scopes.remove(scope)

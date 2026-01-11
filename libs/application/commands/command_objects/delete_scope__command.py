"""Delete scope command."""

from dataclasses import dataclass


@dataclass
class DeleteScopeCommand:
    """Delete scope command."""

    scope_name: str

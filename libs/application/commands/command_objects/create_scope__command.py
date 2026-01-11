"""Create scope command."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateScopeCommand:
    """Create scope command."""

    scope_name: str
    description: Optional[str]

"""Create resource command."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CreateResourceCommand:
    """Create resource command."""

    resource_name: str
    resource_uri: str
    scopes: List[str]
    description: Optional[str]

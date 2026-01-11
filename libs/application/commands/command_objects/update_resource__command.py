"""Update resource command."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UpdateResourceCommand:
    """Update resource command."""

    resource_id: str
    resource_name: Optional[str]
    resource_uri: Optional[str]
    scopes: Optional[List[str]]
    description: Optional[str]
    is_active: Optional[bool]

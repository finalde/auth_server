"""Update client command."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UpdateClientCommand:
    """Update client command."""

    client_id: str
    client_name: Optional[str]
    client_uri: Optional[str]
    redirect_uris: Optional[List[str]]
    grant_types: Optional[List[str]]
    response_types: Optional[List[str]]
    scopes: Optional[List[str]]
    logo_uri: Optional[str]
    tos_uri: Optional[str]
    policy_uri: Optional[str]
    is_active: Optional[bool]

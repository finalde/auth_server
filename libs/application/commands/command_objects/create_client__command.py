"""Create client command."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CreateClientCommand:
    """Create client command."""

    client_name: Optional[str]
    client_uri: Optional[str]
    redirect_uris: List[str]
    grant_types: List[str]
    response_types: List[str]
    scopes: List[str]
    logo_uri: Optional[str]
    tos_uri: Optional[str]
    policy_uri: Optional[str]

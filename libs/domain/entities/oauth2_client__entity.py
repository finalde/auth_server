"""OAuth2 Client entity."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class OAuth2Client:
    """OAuth2 Client domain entity."""

    client_id: str
    client_secret: str
    redirect_uris: List[str] = field(default_factory=list)
    grant_types: List[str] = field(default_factory=list)
    response_types: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    client_name: str = ""
    client_uri: str = ""
    logo_uri: str = ""
    tos_uri: str = ""
    policy_uri: str = ""
    is_active: bool = True

    def add_redirect_uri(self, redirect_uri: str) -> None:
        """Add redirect URI."""
        if redirect_uri not in self.redirect_uris:
            self.redirect_uris.append(redirect_uri)

    def remove_redirect_uri(self, redirect_uri: str) -> None:
        """Remove redirect URI."""
        if redirect_uri in self.redirect_uris:
            self.redirect_uris.remove(redirect_uri)

    def add_grant_type(self, grant_type: str) -> None:
        """Add grant type."""
        if grant_type not in self.grant_types:
            self.grant_types.append(grant_type)

    def add_scope(self, scope: str) -> None:
        """Add scope."""
        if scope not in self.scopes:
            self.scopes.append(scope)

"""Delete client command."""

from dataclasses import dataclass


@dataclass
class DeleteClientCommand:
    """Delete client command."""

    client_id: str

"""Delete resource command."""

from dataclasses import dataclass


@dataclass
class DeleteResourceCommand:
    """Delete resource command."""

    resource_id: str

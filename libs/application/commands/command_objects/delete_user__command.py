"""Delete user command."""

from dataclasses import dataclass


@dataclass
class DeleteUserCommand:
    """Delete user command."""

    user_id: str

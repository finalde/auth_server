"""Create user command."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateUserCommand:
    """Create user command."""

    username: str
    email: str
    password: str
    first_name: Optional[str]
    last_name: Optional[str]

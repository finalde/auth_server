"""Update user command."""

from dataclasses import dataclass
from typing import Optional

from libs.common.enums import UserStatusEnum


@dataclass
class UpdateUserCommand:
    """Update user command."""

    user_id: str
    username: Optional[str]
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    status: Optional[UserStatusEnum]
    is_active: Optional[bool]

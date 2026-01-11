"""User entity."""

from dataclasses import dataclass

from libs.common.enums import UserStatusEnum


@dataclass
class User:
    """User domain entity."""

    user_id: str
    username: str
    email: str
    password_hash: str
    status: UserStatusEnum = UserStatusEnum.ACTIVE
    first_name: str = ""
    last_name: str = ""
    is_active: bool = True

    def activate(self) -> None:
        """Activate user."""
        self.is_active = True
        self.status = UserStatusEnum.ACTIVE

    def deactivate(self) -> None:
        """Deactivate user."""
        self.is_active = False
        self.status = UserStatusEnum.INACTIVE

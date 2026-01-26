"""User scope DTOs."""

from typing import Optional

from pydantic import BaseModel


class UserScopeDTO(BaseModel):
    """User scope DTO."""

    user_id: str
    scope_name: str
    is_active: bool = True


class CreateUserScopeDTO(BaseModel):
    """Create user scope DTO."""

    user_id: str
    scope_name: str


class UpdateUserScopeDTO(BaseModel):
    """Update user scope DTO."""

    is_active: Optional[bool] = None

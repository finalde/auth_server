"""User DTOs."""

from typing import Optional

from libs.common.enums import UserStatusEnum
from pydantic import BaseModel, EmailStr, Field


class UserDTO(BaseModel):
    """User DTO."""

    user_id: str
    username: str
    email: EmailStr
    status: UserStatusEnum
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True

    class Config:
        """Pydantic config."""

        from_attributes = True


class CreateUserDTO(BaseModel):
    """Create user DTO."""

    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UpdateUserDTO(BaseModel):
    """Update user DTO."""

    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    status: Optional[UserStatusEnum] = None
    is_active: Optional[bool] = None

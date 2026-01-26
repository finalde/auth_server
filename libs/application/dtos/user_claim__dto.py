"""User claim DTOs."""

from typing import Optional

from pydantic import BaseModel


class UserClaimDTO(BaseModel):
    """User claim DTO."""

    user_id: str
    claim_name: str
    claim_value: str
    claim_type: Optional[str] = None
    is_active: bool = True


class CreateUserClaimDTO(BaseModel):
    """Create user claim DTO."""

    user_id: str
    claim_name: str
    claim_value: str
    claim_type: Optional[str] = None


class UpdateUserClaimDTO(BaseModel):
    """Update user claim DTO."""

    claim_value: Optional[str] = None
    claim_type: Optional[str] = None
    is_active: Optional[bool] = None

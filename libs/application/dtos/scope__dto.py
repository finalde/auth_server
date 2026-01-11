"""Scope DTOs."""

from typing import Optional

from pydantic import BaseModel, Field


class ScopeDTO(BaseModel):
    """Scope DTO."""

    scope_name: str
    description: Optional[str] = None
    is_active: bool = True

    class Config:
        """Pydantic config."""

        from_attributes = True


class CreateScopeDTO(BaseModel):
    """Create scope DTO."""

    scope_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

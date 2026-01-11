"""Resource DTOs."""

from typing import List, Optional

from pydantic import BaseModel, Field


class ResourceDTO(BaseModel):
    """Resource DTO."""

    resource_id: str
    resource_name: str
    resource_uri: str
    scopes: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    is_active: bool = True

    class Config:
        """Pydantic config."""

        from_attributes = True


class CreateResourceDTO(BaseModel):
    """Create resource DTO."""

    resource_name: str = Field(..., min_length=1, max_length=255)
    resource_uri: str = Field(..., min_length=1)
    scopes: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class UpdateResourceDTO(BaseModel):
    """Update resource DTO."""

    resource_name: Optional[str] = Field(None, min_length=1, max_length=255)
    resource_uri: Optional[str] = Field(None, min_length=1)
    scopes: Optional[List[str]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

"""Client DTOs."""

from typing import List, Optional

from pydantic import BaseModel, Field


class ClientDTO(BaseModel):
    """Client DTO."""

    client_id: str
    client_name: Optional[str] = None
    client_uri: Optional[str] = None
    redirect_uris: List[str] = Field(default_factory=list)
    grant_types: List[str] = Field(default_factory=list)
    response_types: List[str] = Field(default_factory=list)
    scopes: List[str] = Field(default_factory=list)
    logo_uri: Optional[str] = None
    tos_uri: Optional[str] = None
    policy_uri: Optional[str] = None
    is_active: bool = True

    class Config:
        """Pydantic config."""

        from_attributes = True


class CreateClientDTO(BaseModel):
    """Create client DTO."""

    client_name: Optional[str] = None
    client_uri: Optional[str] = None
    redirect_uris: List[str] = Field(default_factory=list)
    grant_types: List[str] = Field(default_factory=list)
    response_types: List[str] = Field(default_factory=list)
    scopes: List[str] = Field(default_factory=list)
    logo_uri: Optional[str] = None
    tos_uri: Optional[str] = None
    policy_uri: Optional[str] = None


class UpdateClientDTO(BaseModel):
    """Update client DTO."""

    client_name: Optional[str] = None
    client_uri: Optional[str] = None
    redirect_uris: Optional[List[str]] = None
    grant_types: Optional[List[str]] = None
    response_types: Optional[List[str]] = None
    scopes: Optional[List[str]] = None
    logo_uri: Optional[str] = None
    tos_uri: Optional[str] = None
    policy_uri: Optional[str] = None
    is_active: Optional[bool] = None


class ClientSecretDTO(BaseModel):
    """Client secret DTO."""

    client_id: str
    client_secret: str

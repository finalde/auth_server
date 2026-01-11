"""Data Transfer Objects."""

from libs.application.dtos.client__dto import (
    ClientDTO,
    ClientSecretDTO,
    CreateClientDTO,
    UpdateClientDTO,
)
from libs.application.dtos.resource__dto import (
    CreateResourceDTO,
    ResourceDTO,
    UpdateResourceDTO,
)
from libs.application.dtos.scope__dto import CreateScopeDTO, ScopeDTO
from libs.application.dtos.user__dto import CreateUserDTO, UpdateUserDTO, UserDTO

__all__ = [
    "ClientDTO",
    "CreateClientDTO",
    "UpdateClientDTO",
    "ClientSecretDTO",
    "UserDTO",
    "CreateUserDTO",
    "UpdateUserDTO",
    "ResourceDTO",
    "CreateResourceDTO",
    "UpdateResourceDTO",
    "ScopeDTO",
    "CreateScopeDTO",
]

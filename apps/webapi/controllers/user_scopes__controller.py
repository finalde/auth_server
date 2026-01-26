"""User scopes controller."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from apps.webapi.dependencies import get_user_scope_service
from apps.webapi.routes import USER_SCOPES_BASE
from libs.application.dtos.user_scope__dto import (
    CreateUserScopeDTO,
    UpdateUserScopeDTO,
    UserScopeDTO,
)
from libs.application.services.user_scope__service import UserScopeService

router: APIRouter = APIRouter(prefix=USER_SCOPES_BASE, tags=["user-scopes"])


@router.get("/", response_model=List[UserScopeDTO])
async def get_all_user_scopes_async(
    service: UserScopeService = Depends(get_user_scope_service),
) -> List[UserScopeDTO]:
    """Get all user scopes."""
    return await service.get_all_async()


@router.post("/", response_model=UserScopeDTO, status_code=status.HTTP_201_CREATED)
async def create_user_scope_async(
    create_dto: CreateUserScopeDTO,
    service: UserScopeService = Depends(get_user_scope_service),
) -> UserScopeDTO:
    """Create a user scope."""
    return await service.create_async(create_dto)


@router.put("/{user_id}/{scope_name}", response_model=UserScopeDTO)
async def update_user_scope_async(
    user_id: str,
    scope_name: str,
    update_dto: UpdateUserScopeDTO,
    service: UserScopeService = Depends(get_user_scope_service),
) -> UserScopeDTO:
    """Update a user scope."""
    updated = await service.update_async(user_id, scope_name, update_dto)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User scope {scope_name} for user {user_id} not found",
        )
    return updated


@router.delete("/{user_id}/{scope_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_scope_async(
    user_id: str,
    scope_name: str,
    service: UserScopeService = Depends(get_user_scope_service),
) -> None:
    """Delete a user scope."""
    await service.delete_async(user_id, scope_name)

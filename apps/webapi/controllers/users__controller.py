"""Users controller."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status

from libs.application.commands.command_dispatcher import CommandDispatcher
from libs.application.commands.command_objects import (
    CreateUserCommand,
    DeleteUserCommand,
    UpdateUserCommand,
)
from libs.application.dtos.user__dto import (
    UserDTO,
    CreateUserDTO,
    UpdateUserDTO,
)
from libs.application.queries.user_query import IUserQuery
from libs.infrastructure.authorization import Authorize
from apps.webapi.dependencies import get_command_dispatcher, get_user_query
from apps.webapi.policies import AdminScopePolicy
from apps.webapi.routes import API_BASE

router: APIRouter = APIRouter(prefix=f"{API_BASE}/users", tags=["users"])


@router.get("/", response_model=List[UserDTO])
@Authorize(policy=AdminScopePolicy())
async def get_all_users_async(
    request: Request,
    query: IUserQuery = Depends(get_user_query),
) -> List[UserDTO]:
    """Get all users."""
    return await query.get_all_async()


@router.get("/{user_id}", response_model=UserDTO)
@Authorize(policy=AdminScopePolicy())
async def get_user_by_id_async(
    request: Request,
    user_id: str,
    query: IUserQuery = Depends(get_user_query),
) -> UserDTO:
    """Get user by ID."""
    user: UserDTO | None = await query.get_by_id_async(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return user


@router.post("/", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
@Authorize(policy=AdminScopePolicy())
async def create_user_async(
    request: Request,
    create_dto: CreateUserDTO,
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> UserDTO:
    """Create a new user."""
    from libs.application.commands.command_objects.create_user__command import (
        CreateUserCommand,
    )
    command = CreateUserCommand(
        username=create_dto.username,
        email=create_dto.email,
        password=create_dto.password,
        first_name=create_dto.first_name,
        last_name=create_dto.last_name,
    )
    result: UserDTO = await dispatcher.dispatch_async(command)
    return result


@router.put("/{user_id}", response_model=UserDTO)
@Authorize(policy=AdminScopePolicy())
async def update_user_async(
    request: Request,
    user_id: str,
    update_dto: UpdateUserDTO,
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> UserDTO:
    """Update user."""
    from libs.application.commands.command_objects.update_user__command import (
        UpdateUserCommand,
    )
    command = UpdateUserCommand(
        user_id=user_id,
        username=update_dto.username,
        email=update_dto.email,
        first_name=update_dto.first_name,
        last_name=update_dto.last_name,
        status=update_dto.status,
        is_active=update_dto.is_active,
    )
    result: UserDTO = await dispatcher.dispatch_async(command)
    return result


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@Authorize(policy=AdminScopePolicy())
async def delete_user_async(
    request: Request,
    user_id: str,
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> None:
    """Delete user."""
    from libs.application.commands.command_objects.delete_user__command import (
        DeleteUserCommand,
    )
    command = DeleteUserCommand(user_id=user_id)
    await dispatcher.dispatch_async(command)

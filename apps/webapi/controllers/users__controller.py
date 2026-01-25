"""Users controller."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

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
from apps.webapi.dependencies import get_command_dispatcher
from apps.webapi.routes import API_BASE

router: APIRouter = APIRouter(prefix=f"{API_BASE}/users", tags=["users"])


@router.get("/", response_model=List[UserDTO])
async def get_all_users_async(
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> List[UserDTO]:
    """Get all users."""
    # TODO: Implement user query
    return []


@router.get("/{user_id}", response_model=UserDTO)
async def get_user_by_id_async(
    user_id: str,
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> UserDTO:
    """Get user by ID."""
    # TODO: Implement user query
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with ID {user_id} not found",
    )


@router.post("/", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
async def create_user_async(
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
async def update_user_async(
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
async def delete_user_async(
    user_id: str,
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> None:
    """Delete user."""
    from libs.application.commands.command_objects.delete_user__command import (
        DeleteUserCommand,
    )
    command = DeleteUserCommand(user_id=user_id)
    await dispatcher.dispatch_async(command)

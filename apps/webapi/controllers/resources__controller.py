"""Resources controller."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from libs.application.commands.command_dispatcher import CommandDispatcher
from libs.application.commands.command_objects import (
    CreateResourceCommand,
    DeleteResourceCommand,
    UpdateResourceCommand,
)
from libs.application.dtos.resource__dto import (
    ResourceDTO,
    CreateResourceDTO,
    UpdateResourceDTO,
)
from apps.webapi.dependencies import get_command_dispatcher
from apps.webapi.routes import API_BASE

router: APIRouter = APIRouter(prefix=f"{API_BASE}/resources", tags=["resources"])


@router.get("/", response_model=List[ResourceDTO])
async def get_all_resources_async(
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> List[ResourceDTO]:
    """Get all resources."""
    # TODO: Implement resource query
    return []


@router.get("/{resource_id}", response_model=ResourceDTO)
async def get_resource_by_id_async(
    resource_id: str,
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> ResourceDTO:
    """Get resource by ID."""
    # TODO: Implement resource query
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Resource with ID {resource_id} not found",
    )


@router.post("/", response_model=ResourceDTO, status_code=status.HTTP_201_CREATED)
async def create_resource_async(
    create_dto: CreateResourceDTO,
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> ResourceDTO:
    """Create a new resource."""
    command = CreateResourceCommand(
        resource_name=create_dto.resource_name,
        resource_uri=create_dto.resource_uri,
        scopes=create_dto.scopes,
        description=create_dto.description,
    )
    result: ResourceDTO = await dispatcher.dispatch_async(command)
    return result


@router.put("/{resource_id}", response_model=ResourceDTO)
async def update_resource_async(
    resource_id: str,
    update_dto: UpdateResourceDTO,
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> ResourceDTO:
    """Update resource."""
    command = UpdateResourceCommand(
        resource_id=resource_id,
        resource_name=update_dto.resource_name,
        resource_uri=update_dto.resource_uri,
        scopes=update_dto.scopes,
        description=update_dto.description,
        is_active=update_dto.is_active,
    )
    result: ResourceDTO = await dispatcher.dispatch_async(command)
    return result


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource_async(
    resource_id: str,
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> None:
    """Delete resource."""
    command = DeleteResourceCommand(resource_id=resource_id)
    await dispatcher.dispatch_async(command)

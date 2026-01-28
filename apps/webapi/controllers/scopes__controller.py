"""Scopes controller."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status

from libs.application.commands.command_dispatcher import CommandDispatcher
from libs.application.commands.command_objects import (
    CreateScopeCommand,
    DeleteScopeCommand,
)
from libs.application.dtos.scope__dto import (
    ScopeDTO,
    CreateScopeDTO,
)
from libs.application.queries.scope_query import IScopeQuery
from libs.infrastructure.authorization import Authorize
from apps.webapi.dependencies import get_command_dispatcher, get_scope_query
from apps.webapi.policies import AdminScopePolicy
from apps.webapi.routes import API_BASE

router: APIRouter = APIRouter(prefix=f"{API_BASE}/scopes", tags=["scopes"])


@router.get("/", response_model=List[ScopeDTO])
@Authorize(policy=AdminScopePolicy())
async def get_all_scopes_async(
    request: Request,
    query: IScopeQuery = Depends(get_scope_query),
) -> List[ScopeDTO]:
    """Get all scopes."""
    return await query.get_all_async()


@router.get("/{scope_name}", response_model=ScopeDTO)
@Authorize(policy=AdminScopePolicy())
async def get_scope_by_name_async(
    request: Request,
    scope_name: str,
    query: IScopeQuery = Depends(get_scope_query),
) -> ScopeDTO:
    """Get scope by name."""
    scope: ScopeDTO | None = await query.get_by_name_async(scope_name)
    if not scope:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scope {scope_name} not found",
        )
    return scope


@router.post("/", response_model=ScopeDTO, status_code=status.HTTP_201_CREATED)
@Authorize(policy=AdminScopePolicy())
async def create_scope_async(
    request: Request,
    create_dto: CreateScopeDTO,
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> ScopeDTO:
    """Create a new scope."""
    command = CreateScopeCommand(
        scope_name=create_dto.scope_name,
        description=create_dto.description,
    )
    result: ScopeDTO = await dispatcher.dispatch_async(command)
    return result


@router.put("/{scope_name}", response_model=ScopeDTO)
@Authorize(policy=AdminScopePolicy())
async def update_scope_async(
    request: Request,
    scope_name: str,
    create_dto: CreateScopeDTO,
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> ScopeDTO:
    """Update scope."""
    # For now, scopes can only be updated via description
    # TODO: Implement scope update command
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Scope update not yet implemented",
    )


@router.delete("/{scope_name}", status_code=status.HTTP_204_NO_CONTENT)
@Authorize(policy=AdminScopePolicy())
async def delete_scope_async(
    request: Request,
    scope_name: str,
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> None:
    """Delete scope."""
    command = DeleteScopeCommand(scope_name=scope_name)
    await dispatcher.dispatch_async(command)

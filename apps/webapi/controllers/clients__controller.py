"""Clients controller."""

from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status

from libs.application.commands.command_dispatcher import CommandDispatcher
from libs.application.commands.command_objects import (
    CreateClientCommand,
    DeleteClientCommand,
    UpdateClientCommand,
)
from libs.application.dtos.client__dto import (
    ClientDTO,
    CreateClientDTO,
    UpdateClientDTO,
)
from libs.application.queries.client_query import IClientQuery
from libs.infrastructure.authorization import Authorize
from apps.webapi.dependencies import get_client_query, get_command_dispatcher
from apps.webapi.policies import AdminScopePolicy
from apps.webapi.routes import API_BASE

router: APIRouter = APIRouter(prefix=f"{API_BASE}/clients", tags=["clients"])


@router.get("/", response_model=List[ClientDTO])
@Authorize(policy=AdminScopePolicy())
async def get_all_clients_async(
    request: Request,
    query: IClientQuery = Depends(get_client_query),
) -> List[ClientDTO]:
    """Get all clients."""
    return await query.get_all_async()


@router.get("/{client_id}", response_model=ClientDTO)
@Authorize(policy=AdminScopePolicy())
async def get_client_by_id_async(
    request: Request,
    client_id: str,
    query: IClientQuery = Depends(get_client_query),
) -> ClientDTO:
    """Get client by ID."""
    client: ClientDTO | None = await query.get_by_id_async(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found",
        )
    return client


@router.post("/", response_model=ClientDTO, status_code=status.HTTP_201_CREATED)
@Authorize(policy=AdminScopePolicy())
async def create_client_async(
    request: Request,
    create_dto: CreateClientDTO,
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> ClientDTO:
    """Create a new client."""
    command: CreateClientCommand = CreateClientCommand(
        client_name=create_dto.client_name,
        client_uri=create_dto.client_uri,
        redirect_uris=create_dto.redirect_uris,
        grant_types=create_dto.grant_types,
        response_types=create_dto.response_types,
        scopes=create_dto.scopes,
        logo_uri=create_dto.logo_uri,
        tos_uri=create_dto.tos_uri,
        policy_uri=create_dto.policy_uri,
    )
    result: ClientDTO = await dispatcher.dispatch_async(command)
    return result


@router.put("/{client_id}", response_model=ClientDTO)
@Authorize(policy=AdminScopePolicy())
async def update_client_async(
    request: Request,
    client_id: str,
    update_dto: UpdateClientDTO,
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> ClientDTO:
    """Update client."""
    command: UpdateClientCommand = UpdateClientCommand(
        client_id=client_id,
        client_name=update_dto.client_name,
        client_uri=update_dto.client_uri,
        redirect_uris=update_dto.redirect_uris,
        grant_types=update_dto.grant_types,
        response_types=update_dto.response_types,
        scopes=update_dto.scopes,
        logo_uri=update_dto.logo_uri,
        tos_uri=update_dto.tos_uri,
        policy_uri=update_dto.policy_uri,
        is_active=update_dto.is_active,
    )
    result: ClientDTO = await dispatcher.dispatch_async(command)
    return result


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
@Authorize(policy=AdminScopePolicy())
async def delete_client_async(
    request: Request,
    client_id: str,
    dispatcher: CommandDispatcher = Depends(get_command_dispatcher),
) -> None:
    """Delete client."""
    command: DeleteClientCommand = DeleteClientCommand(client_id=client_id)
    await dispatcher.dispatch_async(command)

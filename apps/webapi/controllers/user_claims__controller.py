"""User claims controller."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status

from libs.infrastructure.authorization import Authorize
from apps.webapi.dependencies import get_user_claim_service
from apps.webapi.policies import AdminScopePolicy
from apps.webapi.routes import USER_CLAIMS_BASE
from libs.application.dtos.user_claim__dto import (
    CreateUserClaimDTO,
    UpdateUserClaimDTO,
    UserClaimDTO,
)
from libs.application.services.user_claim__service import UserClaimService

router: APIRouter = APIRouter(prefix=USER_CLAIMS_BASE, tags=["user-claims"])


@router.get("/", response_model=List[UserClaimDTO])
@Authorize(policy=AdminScopePolicy())
async def get_all_user_claims_async(
    request: Request,
    service: UserClaimService = Depends(get_user_claim_service),
) -> List[UserClaimDTO]:
    """Get all user claims."""
    return await service.get_all_async()


@router.post("/", response_model=UserClaimDTO, status_code=status.HTTP_201_CREATED)
@Authorize(policy=AdminScopePolicy())
async def create_user_claim_async(
    request: Request,
    create_dto: CreateUserClaimDTO,
    service: UserClaimService = Depends(get_user_claim_service),
) -> UserClaimDTO:
    """Create a user claim."""
    return await service.create_async(create_dto)


@router.put("/{user_id}/{claim_name}", response_model=UserClaimDTO)
@Authorize(policy=AdminScopePolicy())
async def update_user_claim_async(
    request: Request,
    user_id: str,
    claim_name: str,
    update_dto: UpdateUserClaimDTO,
    service: UserClaimService = Depends(get_user_claim_service),
) -> UserClaimDTO:
    """Update a user claim."""
    updated = await service.update_async(user_id, claim_name, update_dto)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User claim {claim_name} for user {user_id} not found",
        )
    return updated


@router.delete("/{user_id}/{claim_name}", status_code=status.HTTP_204_NO_CONTENT)
@Authorize(policy=AdminScopePolicy())
async def delete_user_claim_async(
    request: Request,
    user_id: str,
    claim_name: str,
    service: UserClaimService = Depends(get_user_claim_service),
) -> None:
    """Delete a user claim."""
    await service.delete_async(user_id, claim_name)

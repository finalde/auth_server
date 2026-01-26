"""User claim service."""

from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine

from libs.application.dtos.user_claim__dto import (
    CreateUserClaimDTO,
    UpdateUserClaimDTO,
    UserClaimDTO,
)
from libs.common.interfaces import ILogger


class UserClaimService:
    """Service for managing user claims."""

    def __init__(self, logger: ILogger, database_url: str) -> None:
        """Initialize user claim service."""
        self._logger: ILogger = logger
        self._database_url: str = database_url
        self._engine: Optional[Engine] = None

    def _get_engine(self) -> Engine:
        """Get or create database engine."""
        if self._engine is None:
            self._engine = create_engine(self._database_url, pool_pre_ping=True)
        return self._engine

    async def get_all_async(self) -> List[UserClaimDTO]:
        """Get all user claims."""
        engine = self._get_engine()
        stmt = text(
            """
            SELECT user_id, claim_name, claim_value, claim_type, is_active
            FROM user_claims
            ORDER BY user_id, claim_name
            """
        )
        with engine.connect() as conn:
            rows = conn.execute(stmt).mappings().all()
            return [UserClaimDTO(**row) for row in rows]

    async def create_async(self, create_dto: CreateUserClaimDTO) -> UserClaimDTO:
        """Create a user claim."""
        engine = self._get_engine()
        stmt = text(
            """
            INSERT INTO user_claims (user_id, claim_name, claim_value, claim_type, is_active)
            VALUES (:user_id, :claim_name, :claim_value, :claim_type, TRUE)
            RETURNING user_id, claim_name, claim_value, claim_type, is_active
            """
        )
        payload = create_dto.model_dump()
        with engine.begin() as conn:
            row = conn.execute(stmt, payload).mappings().one()
            return UserClaimDTO(**row)

    async def update_async(
        self, user_id: str, claim_name: str, update_dto: UpdateUserClaimDTO
    ) -> Optional[UserClaimDTO]:
        """Update a user claim."""
        engine = self._get_engine()
        stmt = text(
            """
            UPDATE user_claims
            SET
                claim_value = COALESCE(:claim_value, claim_value),
                claim_type = COALESCE(:claim_type, claim_type),
                is_active = COALESCE(:is_active, is_active)
            WHERE user_id = :user_id AND claim_name = :claim_name
            RETURNING user_id, claim_name, claim_value, claim_type, is_active
            """
        )
        payload = update_dto.model_dump()
        payload.update({"user_id": user_id, "claim_name": claim_name})
        with engine.begin() as conn:
            row = conn.execute(stmt, payload).mappings().one_or_none()
            if not row:
                return None
            return UserClaimDTO(**row)

    async def delete_async(self, user_id: str, claim_name: str) -> None:
        """Delete a user claim."""
        engine = self._get_engine()
        stmt = text(
            """
            DELETE FROM user_claims
            WHERE user_id = :user_id AND claim_name = :claim_name
            """
        )
        with engine.begin() as conn:
            conn.execute(stmt, {"user_id": user_id, "claim_name": claim_name})

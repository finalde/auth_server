"""User scope service."""

from typing import List, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from libs.application.dtos.user_scope__dto import (
    CreateUserScopeDTO,
    UpdateUserScopeDTO,
    UserScopeDTO,
)
from libs.common.interfaces import ILogger


class UserScopeService:
    """Service for managing user scopes."""

    def __init__(self, logger: ILogger, database_url: str) -> None:
        """Initialize user scope service."""
        self._logger: ILogger = logger
        self._database_url: str = database_url
        self._engine: Optional[Engine] = None

    def _get_engine(self) -> Engine:
        """Get or create database engine."""
        if self._engine is None:
            self._engine = create_engine(self._database_url, pool_pre_ping=True)
        return self._engine

    async def get_all_async(self) -> List[UserScopeDTO]:
        """Get all user scopes."""
        engine = self._get_engine()
        stmt = text(
            """
            SELECT user_id, scope_name, is_active
            FROM user_scopes
            ORDER BY user_id, scope_name
            """
        )
        with engine.connect() as conn:
            rows = conn.execute(stmt).mappings().all()
            return [UserScopeDTO(**row) for row in rows]

    async def create_async(self, create_dto: CreateUserScopeDTO) -> UserScopeDTO:
        """Create a user scope."""
        engine = self._get_engine()
        stmt = text(
            """
            INSERT INTO user_scopes (user_id, scope_name, is_active)
            VALUES (:user_id, :scope_name, TRUE)
            RETURNING user_id, scope_name, is_active
            """
        )
        payload = create_dto.model_dump()
        with engine.begin() as conn:
            row = conn.execute(stmt, payload).mappings().one()
            return UserScopeDTO(**row)

    async def update_async(
        self, user_id: str, scope_name: str, update_dto: UpdateUserScopeDTO
    ) -> Optional[UserScopeDTO]:
        """Update a user scope."""
        engine = self._get_engine()
        stmt = text(
            """
            UPDATE user_scopes
            SET is_active = COALESCE(:is_active, is_active)
            WHERE user_id = :user_id AND scope_name = :scope_name
            RETURNING user_id, scope_name, is_active
            """
        )
        payload = update_dto.model_dump()
        payload.update({"user_id": user_id, "scope_name": scope_name})
        with engine.begin() as conn:
            row = conn.execute(stmt, payload).mappings().one_or_none()
            if not row:
                return None
            return UserScopeDTO(**row)

    async def delete_async(self, user_id: str, scope_name: str) -> None:
        """Delete a user scope."""
        engine = self._get_engine()
        stmt = text(
            """
            DELETE FROM user_scopes
            WHERE user_id = :user_id AND scope_name = :scope_name
            """
        )
        with engine.begin() as conn:
            conn.execute(stmt, {"user_id": user_id, "scope_name": scope_name})

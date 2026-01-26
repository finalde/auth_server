"""User authentication service."""

from typing import Optional

import bcrypt
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine

from libs.common.interfaces import ILogger


class UserAuthService:
    """Service for authenticating users."""

    def __init__(self, logger: ILogger, database_url: str) -> None:
        """Initialize auth service."""
        self._logger: ILogger = logger
        self._database_url: str = database_url
        self._engine: Optional[Engine] = None

    def _get_engine(self) -> Engine:
        """Get or create database engine."""
        if self._engine is None:
            self._engine = create_engine(self._database_url, pool_pre_ping=True)
        return self._engine

    async def authenticate_async(self, username: str, password: str) -> bool:
        """Validate username/password against stored hash."""
        engine = self._get_engine()
        stmt = text(
            """
            SELECT password_hash, is_active
            FROM users
            WHERE username = :username
            LIMIT 1
            """
        )
        with engine.connect() as conn:
            row = conn.execute(stmt, {"username": username}).mappings().one_or_none()
            if not row:
                return False
            if not row["is_active"]:
                return False
            stored_hash = row["password_hash"]
            if not stored_hash:
                return False
            try:
                return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
            except ValueError as exc:
                self._logger.error("Invalid password hash format", error=str(exc))
                return False

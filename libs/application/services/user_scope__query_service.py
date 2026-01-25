"""Application service for querying user scopes."""

from typing import Any, Set

from libs.common.interfaces import ILogger


class UserScopeQueryService:
    """Application service for querying user scopes."""

    def __init__(self, logger: ILogger, database_url: str) -> None:
        """Initialize user scope query service."""
        self._logger: ILogger = logger
        self._database_url: str = database_url
        self._engine: Any = None

    def _get_engine(self) -> Any:
        """Get or create database engine."""
        if self._engine is None:
            from sqlalchemy import create_engine
            self._engine = create_engine(self._database_url, pool_pre_ping=True)
        return self._engine

    def get_user_scopes(self, username: str) -> Set[str]:
        """Load active scopes for a given user from user_scopes table.
        
        This constrains which scopes a user is allowed to receive in tokens.
        """
        from sqlalchemy import text
        
        scopes: Set[str] = set()
        engine = self._get_engine()
        
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT us.scope_name
                    FROM user_scopes us
                    JOIN users u ON u.user_id = us.user_id
                    WHERE u.username = :username
                      AND us.is_active = TRUE
                    """
                ),
                {"username": username},
            )
            for row in result:
                scopes.add(row.scope_name)
        
        return scopes

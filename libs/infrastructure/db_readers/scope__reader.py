"""Scope reader implementation."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from libs.common.interfaces import IScopeReader
from libs.infrastructure.data_access_objects.scope__db_dao import ScopeDAO


class ScopeReader(IScopeReader):
    """Scope reader implementation."""

    def __init__(self, session: Session) -> None:
        """Initialize scope reader.

        Args:
            session: SQLAlchemy database session.
        """
        self._session: Session = session

    async def get_by_name_async(self, scope_name: str) -> Optional[ScopeDAO]:
        """Get scope by name.

        Args:
            scope_name: Scope name.

        Returns:
            Scope DAO if found, None otherwise.
        """
        stmt = select(ScopeDAO).where(
            ScopeDAO.scope_name == scope_name,
            ScopeDAO.is_active == True,  # noqa: E712
        )
        try:
            return self._session.execute(stmt).scalar_one_or_none()
        except Exception:
            self._session.rollback()
            raise
        finally:
            self._session.close()

    async def get_all_async(self) -> List[ScopeDAO]:
        """Get all active scopes.

        Returns:
            List of scope DAOs.
        """
        stmt = select(ScopeDAO).where(ScopeDAO.is_active == True)  # noqa: E712
        try:
            result = self._session.execute(stmt).scalars().all()
            return list(result)
        except Exception:
            self._session.rollback()
            raise
        finally:
            self._session.close()

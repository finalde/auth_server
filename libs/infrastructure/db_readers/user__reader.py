"""User reader implementation."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from libs.common.interfaces import IUserReader
from libs.infrastructure.data_access_objects.user__db_dao import UserDAO


class UserReader(IUserReader):
    """User reader implementation."""

    def __init__(self, session: Session) -> None:
        """Initialize user reader.

        Args:
            session: SQLAlchemy database session.
        """
        self._session: Session = session

    async def get_by_id_async(self, user_id: str) -> Optional[UserDAO]:
        """Get user by ID.

        Args:
            user_id: User identifier.

        Returns:
            User DAO if found, None otherwise.
        """
        stmt = select(UserDAO).where(
            UserDAO.user_id == user_id,
            UserDAO.is_active == True,  # noqa: E712
        )
        try:
            return self._session.execute(stmt).scalar_one_or_none()
        except Exception:
            self._session.rollback()
            raise
        finally:
            self._session.close()

    async def get_by_username_async(self, username: str) -> Optional[UserDAO]:
        """Get user by username.

        Args:
            username: Username.

        Returns:
            User DAO if found, None otherwise.
        """
        stmt = select(UserDAO).where(
            UserDAO.username == username,
            UserDAO.is_active == True,  # noqa: E712
        )
        try:
            return self._session.execute(stmt).scalar_one_or_none()
        except Exception:
            self._session.rollback()
            raise
        finally:
            self._session.close()

    async def get_all_async(self) -> List[UserDAO]:
        """Get all active users.

        Returns:
            List of user DAOs.
        """
        stmt = select(UserDAO).where(UserDAO.is_active == True)  # noqa: E712
        try:
            result = self._session.execute(stmt).scalars().all()
            return list(result)
        except Exception:
            self._session.rollback()
            raise
        finally:
            self._session.close()

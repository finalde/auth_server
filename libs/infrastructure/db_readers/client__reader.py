"""Client reader implementation."""

from typing import Any, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from libs.common.interfaces import IClientReader
from libs.infrastructure.data_access_objects.oauth2_client__db_dao import (
    OAuth2ClientDAO,
)


class ClientReader(IClientReader):
    """Client reader implementation."""

    def __init__(self, session: Session) -> None:
        """Initialize client reader.
        
        Args:
            session: SQLAlchemy database session.
        """
        self._session: Session = session

    async def get_by_id_async(self, client_id: str) -> Optional[OAuth2ClientDAO]:
        """Get client by ID.
        
        Args:
            client_id: Client identifier.
        
        Returns:
            Client DAO if found, None otherwise.
        """
        stmt = select(OAuth2ClientDAO).where(
            OAuth2ClientDAO.client_id == client_id,
            OAuth2ClientDAO.is_active == True,  # noqa: E712
        )
        try:
            return self._session.execute(stmt).scalar_one_or_none()
        except Exception:
            self._session.rollback()
            raise
        finally:
            self._session.close()

    async def get_all_async(self) -> List[OAuth2ClientDAO]:
        """Get all active clients.
        
        Returns:
            List of client DAOs.
        """
        stmt = select(OAuth2ClientDAO).where(
            OAuth2ClientDAO.is_active == True  # noqa: E712
        )
        try:
            result = self._session.execute(stmt).scalars().all()
            return list(result)
        except Exception:
            self._session.rollback()
            raise
        finally:
            self._session.close()

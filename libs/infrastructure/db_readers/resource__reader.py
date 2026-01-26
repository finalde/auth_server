"""Resource reader implementation."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from libs.common.interfaces import IResourceReader
from libs.infrastructure.data_access_objects.resource__db_dao import ResourceDAO


class ResourceReader(IResourceReader):
    """Resource reader implementation."""

    def __init__(self, session: Session) -> None:
        """Initialize resource reader.

        Args:
            session: SQLAlchemy database session.
        """
        self._session: Session = session

    async def get_by_id_async(self, resource_id: str) -> Optional[ResourceDAO]:
        """Get resource by ID.

        Args:
            resource_id: Resource identifier.

        Returns:
            Resource DAO if found, None otherwise.
        """
        stmt = select(ResourceDAO).where(
            ResourceDAO.resource_id == resource_id,
            ResourceDAO.is_active == True,  # noqa: E712
        )
        try:
            return self._session.execute(stmt).scalar_one_or_none()
        except Exception:
            self._session.rollback()
            raise
        finally:
            self._session.close()

    async def get_all_async(self) -> List[ResourceDAO]:
        """Get all active resources.

        Returns:
            List of resource DAOs.
        """
        stmt = select(ResourceDAO).where(ResourceDAO.is_active == True)  # noqa: E712
        try:
            result = self._session.execute(stmt).scalars().all()
            return list(result)
        except Exception:
            self._session.rollback()
            raise
        finally:
            self._session.close()

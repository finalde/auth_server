"""User query interface and implementation."""

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from libs.application.dtos.user__dto import UserDTO
from libs.common.interfaces import IUserReader


class IUserQuery(ABC):
    """User query interface."""

    @abstractmethod
    async def get_by_id_async(self, user_id: str) -> Optional[UserDTO]:
        """Get user by ID."""
        pass

    @abstractmethod
    async def get_all_async(self) -> List[UserDTO]:
        """Get all users."""
        pass


class UserQuery(IUserQuery):
    """User query implementation."""

    def __init__(self, reader: IUserReader, mapper: Any) -> None:
        """Initialize user query."""
        self._reader: IUserReader = reader
        self._mapper: Any = mapper

    async def get_by_id_async(self, user_id: str) -> Optional[UserDTO]:
        """Get user by ID."""
        dao: Optional[Any] = await self._reader.get_by_id_async(user_id)
        if not dao:
            return None
        return self._mapper.dao_to_dto(dao)

    async def get_all_async(self) -> List[UserDTO]:
        """Get all users."""
        daos: List[Any] = await self._reader.get_all_async()
        return [self._mapper.dao_to_dto(dao) for dao in daos]

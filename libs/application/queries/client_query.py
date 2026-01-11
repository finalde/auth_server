"""Client query interface and implementation."""

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from libs.application.dtos.client__dto import ClientDTO
from libs.common.interfaces import IClientReader


class IClientQuery(ABC):
    """Client query interface."""

    @abstractmethod
    async def get_by_id_async(self, client_id: str) -> Optional[ClientDTO]:
        """Get client by ID."""
        pass

    @abstractmethod
    async def get_all_async(self) -> List[ClientDTO]:
        """Get all clients."""
        pass


class ClientQuery(IClientQuery):
    """Client query implementation."""

    def __init__(self, reader: IClientReader, mapper: Any) -> None:
        """Initialize client query."""
        self._reader: IClientReader = reader
        self._mapper: Any = mapper

    async def get_by_id_async(self, client_id: str) -> Optional[ClientDTO]:
        """Get client by ID."""
        dao: Optional[Any] = await self._reader.get_by_id_async(client_id)
        if not dao:
            return None
        return self._mapper.dao_to_dto(dao)

    async def get_all_async(self) -> List[ClientDTO]:
        """Get all clients."""
        daos: List[Any] = await self._reader.get_all_async()
        return [self._mapper.dao_to_dto(dao) for dao in daos]

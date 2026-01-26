"""Resource query interface and implementation."""

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from libs.application.dtos.resource__dto import ResourceDTO
from libs.common.interfaces import IResourceReader


class IResourceQuery(ABC):
    """Resource query interface."""

    @abstractmethod
    async def get_by_id_async(self, resource_id: str) -> Optional[ResourceDTO]:
        """Get resource by ID."""
        pass

    @abstractmethod
    async def get_all_async(self) -> List[ResourceDTO]:
        """Get all resources."""
        pass


class ResourceQuery(IResourceQuery):
    """Resource query implementation."""

    def __init__(self, reader: IResourceReader, mapper: Any) -> None:
        """Initialize resource query."""
        self._reader: IResourceReader = reader
        self._mapper: Any = mapper

    async def get_by_id_async(self, resource_id: str) -> Optional[ResourceDTO]:
        """Get resource by ID."""
        dao: Optional[Any] = await self._reader.get_by_id_async(resource_id)
        if not dao:
            return None
        return self._mapper.dao_to_dto(dao)

    async def get_all_async(self) -> List[ResourceDTO]:
        """Get all resources."""
        daos: List[Any] = await self._reader.get_all_async()
        return [self._mapper.dao_to_dto(dao) for dao in daos]

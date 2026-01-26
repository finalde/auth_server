"""Scope query interface and implementation."""

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from libs.application.dtos.scope__dto import ScopeDTO
from libs.common.interfaces import IScopeReader


class IScopeQuery(ABC):
    """Scope query interface."""

    @abstractmethod
    async def get_by_name_async(self, scope_name: str) -> Optional[ScopeDTO]:
        """Get scope by name."""
        pass

    @abstractmethod
    async def get_all_async(self) -> List[ScopeDTO]:
        """Get all scopes."""
        pass


class ScopeQuery(IScopeQuery):
    """Scope query implementation."""

    def __init__(self, reader: IScopeReader, mapper: Any) -> None:
        """Initialize scope query."""
        self._reader: IScopeReader = reader
        self._mapper: Any = mapper

    async def get_by_name_async(self, scope_name: str) -> Optional[ScopeDTO]:
        """Get scope by name."""
        dao: Optional[Any] = await self._reader.get_by_name_async(scope_name)
        if not dao:
            return None
        return self._mapper.dao_to_dto(dao)

    async def get_all_async(self) -> List[ScopeDTO]:
        """Get all scopes."""
        daos: List[Any] = await self._reader.get_all_async()
        return [self._mapper.dao_to_dto(dao) for dao in daos]

"""Scope mapper."""

from libs.application.dtos.scope__dto import ScopeDTO
from libs.domain.entities.scope__entity import Scope
from libs.infrastructure.data_access_objects.scope__db_dao import ScopeDAO


class ScopeMapper:
    """Mapper between Scope domain, DAO, and DTO."""

    @staticmethod
    def dao_to_entity(dao: ScopeDAO) -> Scope:
        """Map DAO to domain entity."""
        return Scope(
            scope_name=dao.scope_name,
            description=dao.description or "",
            is_active=dao.is_active,
        )

    @staticmethod
    def entity_to_dto(entity: Scope) -> ScopeDTO:
        """Map domain entity to DTO."""
        return ScopeDTO(
            scope_name=entity.scope_name,
            description=entity.description if entity.description else None,
            is_active=entity.is_active,
        )

    @staticmethod
    def dao_to_dto(dao: ScopeDAO) -> ScopeDTO:
        """Map DAO directly to DTO."""
        return ScopeDTO(
            scope_name=dao.scope_name,
            description=dao.description,
            is_active=dao.is_active,
        )

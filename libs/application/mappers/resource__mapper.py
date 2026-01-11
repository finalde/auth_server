"""Resource mapper."""

from libs.application.dtos.resource__dto import ResourceDTO
from libs.domain.entities.resource__entity import Resource
from libs.infrastructure.data_access_objects.resource__db_dao import ResourceDAO


class ResourceMapper:
    """Mapper between Resource domain, DAO, and DTO."""

    @staticmethod
    def dao_to_entity(dao: ResourceDAO) -> Resource:
        """Map DAO to domain entity."""
        return Resource(
            resource_id=dao.resource_id,
            resource_name=dao.resource_name,
            resource_uri=dao.resource_uri,
            scopes=dao.scopes or [],
            description=dao.description or "",
            is_active=dao.is_active,
        )

    @staticmethod
    def entity_to_dto(entity: Resource) -> ResourceDTO:
        """Map domain entity to DTO."""
        return ResourceDTO(
            resource_id=entity.resource_id,
            resource_name=entity.resource_name,
            resource_uri=entity.resource_uri,
            scopes=entity.scopes,
            description=entity.description if entity.description else None,
            is_active=entity.is_active,
        )

    @staticmethod
    def dao_to_dto(dao: ResourceDAO) -> ResourceDTO:
        """Map DAO directly to DTO."""
        return ResourceDTO(
            resource_id=dao.resource_id,
            resource_name=dao.resource_name,
            resource_uri=dao.resource_uri,
            scopes=dao.scopes or [],
            description=dao.description,
            is_active=dao.is_active,
        )

"""Client mapper."""

from libs.application.dtos.client__dto import ClientDTO
from libs.domain.entities.oauth2_client__entity import OAuth2Client
from libs.infrastructure.data_access_objects.oauth2_client__db_dao import OAuth2ClientDAO


class ClientMapper:
    """Mapper between Client domain, DAO, and DTO."""

    @staticmethod
    def dao_to_entity(dao: OAuth2ClientDAO) -> OAuth2Client:
        """Map DAO to domain entity."""
        return OAuth2Client(
            client_id=dao.client_id,
            client_secret=dao.client_secret,
            redirect_uris=dao.redirect_uris or [],
            grant_types=dao.grant_types or [],
            response_types=dao.response_types or [],
            scopes=dao.scopes or [],
            client_name=dao.client_name or "",
            client_uri=dao.client_uri or "",
            logo_uri=dao.logo_uri or "",
            tos_uri=dao.tos_uri or "",
            policy_uri=dao.policy_uri or "",
            is_active=dao.is_active,
        )

    @staticmethod
    def entity_to_dto(entity: OAuth2Client) -> ClientDTO:
        """Map domain entity to DTO."""
        return ClientDTO(
            client_id=entity.client_id,
            client_name=entity.client_name if entity.client_name else None,
            client_uri=entity.client_uri if entity.client_uri else None,
            redirect_uris=entity.redirect_uris,
            grant_types=entity.grant_types,
            response_types=entity.response_types,
            scopes=entity.scopes,
            logo_uri=entity.logo_uri if entity.logo_uri else None,
            tos_uri=entity.tos_uri if entity.tos_uri else None,
            policy_uri=entity.policy_uri if entity.policy_uri else None,
            is_active=entity.is_active,
        )

    @staticmethod
    def dao_to_dto(dao: OAuth2ClientDAO) -> ClientDTO:
        """Map DAO directly to DTO."""
        return ClientDTO(
            client_id=dao.client_id,
            client_name=dao.client_name,
            client_uri=dao.client_uri,
            redirect_uris=dao.redirect_uris or [],
            grant_types=dao.grant_types or [],
            response_types=dao.response_types or [],
            scopes=dao.scopes or [],
            logo_uri=dao.logo_uri,
            tos_uri=dao.tos_uri,
            policy_uri=dao.policy_uri,
            is_active=dao.is_active,
        )

    @staticmethod
    def entity_to_dao(entity: OAuth2Client) -> OAuth2ClientDAO:
        """Map domain entity to DAO."""
        return OAuth2ClientDAO(
            client_id=entity.client_id.value,
            client_secret=entity.client_secret,
            redirect_uris=[uri.value for uri in entity.redirect_uris],
            grant_types=entity.grant_types,
            response_types=entity.response_types,
            scopes=entity.scopes,
            client_name=entity.client_name,
            client_uri=entity.client_uri,
            logo_uri=entity.logo_uri,
            tos_uri=entity.tos_uri,
            policy_uri=entity.policy_uri,
            is_active=entity.is_active,
        )

"""User mapper."""

from libs.application.dtos.user__dto import UserDTO
from libs.common.enums import UserStatusEnum
from libs.domain.entities.user__entity import User
from libs.infrastructure.data_access_objects.user__db_dao import UserDAO


class UserMapper:
    """Mapper between User domain, DAO, and DTO."""

    @staticmethod
    def dao_to_entity(dao: UserDAO) -> User:
        """Map DAO to domain entity."""
        return User(
            user_id=dao.user_id,
            username=dao.username,
            email=dao.email,
            password_hash=dao.password_hash,
            status=UserStatusEnum(dao.status),
            first_name=dao.first_name or "",
            last_name=dao.last_name or "",
            is_active=dao.is_active,
        )

    @staticmethod
    def entity_to_dto(entity: User) -> UserDTO:
        """Map domain entity to DTO."""
        return UserDTO(
            user_id=entity.user_id,
            username=entity.username,
            email=entity.email,
            status=entity.status,
            first_name=entity.first_name if entity.first_name else None,
            last_name=entity.last_name if entity.last_name else None,
            is_active=entity.is_active,
        )

    @staticmethod
    def dao_to_dto(dao: UserDAO) -> UserDTO:
        """Map DAO directly to DTO."""
        return UserDTO(
            user_id=dao.user_id,
            username=dao.username,
            email=dao.email,
            status=UserStatusEnum(dao.status),
            first_name=dao.first_name,
            last_name=dao.last_name,
            is_active=dao.is_active,
        )

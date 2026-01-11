"""User DAO."""

from sqlalchemy import Boolean, Column, String

from libs.common.enums import UserStatusEnum
from libs.infrastructure.data_access_objects.base__db_dao import BaseDAO


class UserDAO(BaseDAO):
    """User database model."""

    __tablename__ = "users"

    user_id: Column = Column(String(36), unique=True, nullable=False, index=True)
    username: Column = Column(String(100), unique=True, nullable=False, index=True)
    email: Column = Column(String(255), unique=True, nullable=False, index=True)
    password_hash: Column = Column(String(255), nullable=False)
    status: Column = Column(String(20), default=UserStatusEnum.ACTIVE.value, nullable=False)
    first_name: Column = Column(String(100))
    last_name: Column = Column(String(100))
    is_active: Column = Column(Boolean, default=True, nullable=False)

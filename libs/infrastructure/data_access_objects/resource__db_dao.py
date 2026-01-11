"""Resource DAO."""

from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.dialects.postgresql import ARRAY

from libs.infrastructure.data_access_objects.base__db_dao import BaseDAO


class ResourceDAO(BaseDAO):
    """Resource database model."""

    __tablename__ = "resources"

    resource_id: Column = Column(String(36), unique=True, nullable=False, index=True)
    resource_name: Column = Column(String(255), nullable=False)
    resource_uri: Column = Column(String(512), nullable=False, index=True)
    scopes: Column = Column(ARRAY(String))
    description: Column = Column(Text)
    is_active: Column = Column(Boolean, default=True, nullable=False)

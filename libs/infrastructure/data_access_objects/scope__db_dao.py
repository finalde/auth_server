"""Scope DAO."""

from sqlalchemy import Boolean, Column, String, Text

from libs.infrastructure.data_access_objects.base__db_dao import BaseDAO


class ScopeDAO(BaseDAO):
    """Scope database model."""

    __tablename__ = "scopes"

    # scopes table uses scope_name as primary key; disable BaseDAO.id mapping
    id = None

    scope_name = Column(String(100), unique=True, nullable=False, primary_key=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)

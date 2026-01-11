"""Scope DAO."""

from sqlalchemy import Boolean, Column, String, Text

from libs.infrastructure.data_access_objects.base__db_dao import BaseDAO


class ScopeDAO(BaseDAO):
    """Scope database model."""

    __tablename__ = "scopes"

    scope_name: Column = Column(String(100), unique=True, nullable=False, primary_key=True)
    description: Column = Column(Text)
    is_active: Column = Column(Boolean, default=True, nullable=False)

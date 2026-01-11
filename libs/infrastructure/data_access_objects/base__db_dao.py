"""Base DAO class."""

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class BaseDAO(Base):
    """Base DAO class."""

    __abstract__ = True

    id: Column = Column(String(36), primary_key=True)
    created_at: Column = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Column = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

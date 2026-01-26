"""Base DAO class."""

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all DAOs with legacy annotation support."""
    __allow_unmapped__ = True  # Allow legacy SQLAlchemy annotations


class BaseDAO(Base):
    """Base DAO class."""

    __abstract__ = True

    id = Column(String(36), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

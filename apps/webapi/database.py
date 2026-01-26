"""Database session management for WebAPI."""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from libs.common.interfaces import IAppConfig


def create_database_engine(config: IAppConfig) -> Engine:
    """Create a database engine.

    Args:
        config: Application configuration containing database URL.

    Returns:
        SQLAlchemy engine instance.
    """
    database_url: str = config.get_database_url()
    return create_engine(database_url, pool_pre_ping=True)


def create_session_factory(engine: Engine) -> sessionmaker:
    """Create a session factory.

    Args:
        engine: SQLAlchemy engine.

    Returns:
        Session factory.
    """
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def create_database_session(session_factory: sessionmaker) -> Session:
    """Create a database session.

    Args:
        session_factory: Session factory.

    Returns:
        Database session instance.
    """
    return session_factory()

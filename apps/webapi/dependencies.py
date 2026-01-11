"""FastAPI dependency injection setup."""

from typing import Generator

from fastapi import Depends
from libs.common.di_container import DIContainer

# Global DI container instance
_container: DIContainer = DIContainer()


def get_container() -> DIContainer:
    """Get DI container instance."""
    return _container


def init_container() -> None:
    """Initialize DI container with services."""
    # Register services here
    pass

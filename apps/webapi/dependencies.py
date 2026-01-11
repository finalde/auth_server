"""FastAPI dependency injection setup."""

from typing import Generator, Optional

from fastapi import Depends
from libs.common.di_container import DIContainer
from libs.common.interfaces import IAppConfig

from apps.webapi.di_container import configure_container

# Global DI container instance
_container: DIContainer = DIContainer()
_initialized: bool = False


def get_container() -> DIContainer:
    """Get DI container instance."""
    if not _initialized:
        init_container()
    return _container


def init_container(config_path: Optional[str] = None) -> None:
    """Initialize DI container with services."""
    global _initialized
    configure_container(_container, config_path=config_path)
    _initialized = True


def get_config() -> IAppConfig:
    """Get application configuration from DI container."""
    container: DIContainer = get_container()
    return container.resolve(IAppConfig)

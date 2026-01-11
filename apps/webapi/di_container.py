"""WebAPI DI container configuration."""

from libs.common.di_container import DIContainer
from libs.common.interfaces import IAppConfig, ILogger
from libs.common.logger import Logger

from apps.webapi.app_config import WebAPIConfig


def configure_container(container: DIContainer, database_url: str) -> None:
    """Configure DI container for WebAPI."""
    # Register configuration
    config: IAppConfig = WebAPIConfig(database_url=database_url)
    container.register_singleton(IAppConfig, config)

    # Register logger
    logger: ILogger = Logger(name="auth_server")
    container.register_singleton(ILogger, logger)

    # Register other services here
    # container.register_transient(ISomeService, SomeService)

"""WebAPI DI container configuration."""

from typing import Optional

from libs.common.di_container import DIContainer
from libs.common.interfaces import IAppConfig, ILogger
from libs.common.logger import Logger

from apps.webapi.app_config import WebAPIConfig


def configure_container(
    container: DIContainer, config_path: Optional[str] = None
) -> None:
    """Configure DI container for WebAPI."""
    # Register configuration (reads from config.yml)
    config: IAppConfig = WebAPIConfig(config_path=config_path)
    container.register_singleton(IAppConfig, config)

    # Register logger
    logger: ILogger = Logger(name="auth_server", level=config.get_log_level())
    container.register_singleton(ILogger, logger)

    # Register other services here
    # container.register_transient(ISomeService, SomeService)

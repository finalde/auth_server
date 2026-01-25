"""WebAPI DI container configuration using dependency-injector.

This module configures the dependency injection container for the WebAPI application.
All services, readers, writers, queries, and commands are registered here.
"""

from dependency_injector import containers, providers
from typing import Optional

from libs.common.di_container import BaseContainer
from libs.common.interfaces import (
    IAppConfig,
    IClientReader,
    IClientWriter,
    ILogger,
    IResourceReader,
    IResourceWriter,
    IScopeReader,
    IScopeWriter,
    IUserReader,
    IUserWriter,
)

from apps.webapi.app_config import WebAPIConfig
from libs.application.services.oidc__orchestration_service import (
    IOIDCOrchestrationService,
    OIDCOrchestrationService,
)
from libs.application.services.oidc_authorization__orchestration_service import (
    IOIDCAuthorizationOrchestrationService,
    OIDCAuthorizationOrchestrationService,
)
from libs.application.services.oidc_discovery__query_service import (
    IOIDCDiscoveryQueryService,
    OIDCDiscoveryQueryService,
)
from libs.application.services.oidc_response__converter import OIDCResponseConverter
from libs.application.services.oidc_token__orchestration_service import (
    IOIDCTokenOrchestrationService,
    OIDCTokenOrchestrationService,
)
from libs.application.services.user_scope__query_service import (
    IUserScopeQueryService,
    UserScopeQueryService,
)
from libs.common.logger import Logger


class WebAPIContainer(BaseContainer):
    """WebAPI dependency injection container."""
    
    # Configuration - WebAPIConfig implements IAppConfig
    # Register as IAppConfig so it can be resolved by interface
    app_config = providers.Singleton(
        WebAPIConfig,
        config_path=None,  # Will be set during initialization
    )
    
    # Also provide as 'config' for backward compatibility
    config = app_config
    
    # Logger - Logger implements ILogger
    # Register as ILogger so it can be resolved by interface
    logger_interface = providers.Singleton(
        Logger,
        name="auth_server",
        level=app_config.provided.get_log_level.call(),
    )
    
    # Also provide as 'logger' for backward compatibility
    logger = logger_interface
    
    # OIDC Orchestration Services
    oidc_orchestration_service = providers.Singleton(
        OIDCOrchestrationService,
        logger=logger_interface,
    )
    
    # User Scope Query Service
    user_scope_query_service = providers.Singleton(
        UserScopeQueryService,
        logger=logger_interface,
        database_url=app_config.provided.get_database_url.call(),
    )
    
    # OIDC Discovery Query Service
    oidc_discovery_query_service = providers.Singleton(
        OIDCDiscoveryQueryService,
        logger=logger_interface,
        oidc_orchestration_service=oidc_orchestration_service,
    )
    
    # OIDC Authorization Orchestration Service
    oidc_authorization_orchestration_service = providers.Factory(
        OIDCAuthorizationOrchestrationService,
        logger=logger_interface,
        oidc_orchestration_service=oidc_orchestration_service,
        user_scope_query_service=user_scope_query_service,
    )
    
    # OIDC Token Orchestration Service
    oidc_token_orchestration_service = providers.Factory(
        OIDCTokenOrchestrationService,
        logger=logger_interface,
        oidc_orchestration_service=oidc_orchestration_service,
    )
    
    # Database session provider (will be implemented when we add database session management)
    # database_session = providers.Factory(...)
    
    # Infrastructure: Readers
    # client_reader = providers.Factory(
    #     ClientReader,
    #     session=database_session,
    # )
    
    # Infrastructure: Writers
    # client_writer = providers.Factory(
    #     ClientWriter,
    #     session=database_session,
    # )
    
    # Application: Mappers
    # client_mapper = providers.Singleton(ClientMapper)
    
    # Application: Queries
    # client_query = providers.Factory(
    #     ClientQuery,
    #     reader=client_reader,
    #     mapper=client_mapper,
    # )
    
    # Application: Command Handlers
    # create_client_handler = providers.Factory(
    #     CreateClientCommandHandler,
    #     writer=client_writer,
    #     mapper=client_mapper,
    # )


# Global container instance
_container: Optional[WebAPIContainer] = None


def get_container(config_path: Optional[str] = None) -> WebAPIContainer:
    """Get or create the WebAPI DI container.
    
    Args:
        config_path: Optional path to configuration file. If None, uses default.
    
    Returns:
        Configured WebAPI container instance.
    """
    global _container
    
    if _container is None:
        _container = WebAPIContainer()
        # Set config path if provided
        if config_path:
            _container.app_config.override(config_path=config_path)
        # Wire the container (required for dependency-injector)
        _container.wire(modules=[
            __name__,
            "apps.webapi.dependencies",
            "apps.webapi.controllers",
        ])
    
    return _container


def reset_container() -> None:
    """Reset the global container (useful for testing)."""
    global _container
    if _container is not None:
        _container.unwire()
    _container = None

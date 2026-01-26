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
from apps.webapi.database import (
    create_database_engine,
    create_database_session,
    create_session_factory,
)
from libs.application.mappers.client__mapper import ClientMapper
from libs.application.mappers.resource__mapper import ResourceMapper
from libs.application.mappers.scope__mapper import ScopeMapper
from libs.application.mappers.user__mapper import UserMapper
from libs.application.queries.client_query import ClientQuery
from libs.application.queries.resource_query import ResourceQuery
from libs.application.queries.scope_query import ScopeQuery
from libs.application.queries.user_query import UserQuery
from libs.application.services.oidc__orchestration_service import (
    OIDCOrchestrationService,
)
from libs.application.services.oidc_authorization__orchestration_service import (
    OIDCAuthorizationOrchestrationService,
)
from libs.application.services.oidc_discovery__query_service import (
    OIDCDiscoveryQueryService,
)
from libs.application.services.oidc_response__converter import OIDCResponseConverter
from libs.application.services.oidc_token__orchestration_service import (
    OIDCTokenOrchestrationService,
)
from libs.application.services.user_auth__service import UserAuthService
from libs.application.services.user_claim__service import UserClaimService
from libs.application.services.user_scope__service import UserScopeService
from libs.application.services.user_scope__query_service import (
    UserScopeQueryService,
)
from libs.common.logger import Logger
from libs.infrastructure.db_readers.client__reader import ClientReader
from libs.infrastructure.db_readers.resource__reader import ResourceReader
from libs.infrastructure.db_readers.scope__reader import ScopeReader
from libs.infrastructure.db_readers.user__reader import UserReader


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

    user_claim_service = providers.Singleton(
        UserClaimService,
        logger=logger_interface,
        database_url=app_config.provided.get_database_url.call(),
    )

    user_scope_service = providers.Singleton(
        UserScopeService,
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

    user_auth_service = providers.Singleton(
        UserAuthService,
        logger=logger_interface,
        database_url=app_config.provided.get_database_url.call(),
    )
    
    # Database session provider
    database_engine = providers.Singleton(
        create_database_engine,
        config=app_config,
    )
    session_factory = providers.Singleton(
        create_session_factory,
        engine=database_engine,
    )
    database_session = providers.Factory(
        create_database_session,
        session_factory=session_factory,
    )
    
    # Infrastructure: Readers
    client_reader = providers.Factory(
        ClientReader,
        session=database_session,
    )
    user_reader = providers.Factory(
        UserReader,
        session=database_session,
    )
    resource_reader = providers.Factory(
        ResourceReader,
        session=database_session,
    )
    scope_reader = providers.Factory(
        ScopeReader,
        session=database_session,
    )
    
    # Infrastructure: Writers
    # client_writer = providers.Factory(
    #     ClientWriter,
    #     session=database_session,
    # )
    
    # Application: Mappers (singletons - stateless)
    client_mapper = providers.Singleton(ClientMapper)
    user_mapper = providers.Singleton(UserMapper)
    resource_mapper = providers.Singleton(ResourceMapper)
    scope_mapper = providers.Singleton(ScopeMapper)
    
    # Application: Queries
    client_query = providers.Factory(
        ClientQuery,
        reader=client_reader,
        mapper=client_mapper,
    )
    user_query = providers.Factory(
        UserQuery,
        reader=user_reader,
        mapper=user_mapper,
    )
    resource_query = providers.Factory(
        ResourceQuery,
        reader=resource_reader,
        mapper=resource_mapper,
    )
    scope_query = providers.Factory(
        ScopeQuery,
        reader=scope_reader,
        mapper=scope_mapper,
    )
    
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

"""FastAPI dependency injection setup using dependency-injector."""

from typing import Optional

from fastapi import Depends
from libs.application.commands.command_dispatcher import CommandDispatcher
from libs.application.services.oidc__orchestration_service import (
    OIDCOrchestrationService,
)
from libs.application.services.oidc_authorization__orchestration_service import (
    OIDCAuthorizationOrchestrationService,
)
from libs.application.services.oidc_discovery__query_service import (
    OIDCDiscoveryQueryService,
)
from libs.application.services.oidc_token__orchestration_service import (
    OIDCTokenOrchestrationService,
)
from libs.common.interfaces import IAppConfig, ILogger

from apps.webapi.di_container import get_container


def get_config() -> IAppConfig:
    """Get application configuration from DI container.
    
    This is a FastAPI dependency that can be used with Depends().
    """
    container = get_container()
    return container.app_config()


def get_logger() -> ILogger:
    """Get logger from DI container.
    
    This is a FastAPI dependency that can be used with Depends().
    """
    container = get_container()
    return container.logger_interface()


# OIDC Service dependencies
def get_oidc_orchestration_service() -> OIDCOrchestrationService:
    """Get OIDC orchestration service from DI container."""
    container = get_container()
    return container.oidc_orchestration_service()


def get_oidc_discovery_query_service() -> OIDCDiscoveryQueryService:
    """Get OIDC discovery query service from DI container."""
    container = get_container()
    return container.oidc_discovery_query_service()


def get_oidc_authorization_orchestration_service() -> OIDCAuthorizationOrchestrationService:
    """Get OIDC authorization orchestration service from DI container."""
    container = get_container()
    return container.oidc_authorization_orchestration_service()


def get_oidc_token_orchestration_service() -> OIDCTokenOrchestrationService:
    """Get OIDC token orchestration service from DI container."""
    container = get_container()
    return container.oidc_token_orchestration_service()


def get_command_dispatcher() -> CommandDispatcher:
    """Get command dispatcher from DI container."""
    container = get_container()
    logger = container.logger_interface()
    return CommandDispatcher(logger=logger)


# Query dependencies (will be added as we implement readers/writers)
# def get_client_query() -> IClientQuery:
#     """Get client query from DI container."""
#     container = get_container()
#     return container.client_query()

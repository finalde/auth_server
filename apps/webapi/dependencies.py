"""FastAPI dependency injection setup using dependency-injector."""

from typing import Optional

from fastapi import Depends
from libs.application.commands.command_dispatcher import CommandDispatcher
from libs.application.queries.client_query import IClientQuery
from libs.application.queries.resource_query import IResourceQuery
from libs.application.queries.scope_query import IScopeQuery
from libs.application.queries.user_query import IUserQuery
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
from libs.application.services.user_auth__service import UserAuthService
from libs.application.services.user_claim__service import UserClaimService
from libs.application.services.user_scope__service import UserScopeService
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


def get_user_auth_service() -> UserAuthService:
    """Get user auth service from DI container."""
    container = get_container()
    return container.user_auth_service()


def get_user_claim_service() -> UserClaimService:
    """Get user claim service from DI container."""
    container = get_container()
    return container.user_claim_service()


def get_user_scope_service() -> UserScopeService:
    """Get user scope service from DI container."""
    container = get_container()
    return container.user_scope_service()


def get_command_dispatcher() -> CommandDispatcher:
    """Get command dispatcher from DI container."""
    container = get_container()
    logger = container.logger_interface()
    return CommandDispatcher(logger=logger)


# Query dependencies
def get_client_query() -> IClientQuery:
    """Get client query from DI container."""
    container = get_container()
    return container.client_query()


def get_user_query() -> IUserQuery:
    """Get user query from DI container."""
    container = get_container()
    return container.user_query()


def get_resource_query() -> IResourceQuery:
    """Get resource query from DI container."""
    container = get_container()
    return container.resource_query()


def get_scope_query() -> IScopeQuery:
    """Get scope query from DI container."""
    container = get_container()
    return container.scope_query()

"""Dependency injection container using dependency-injector library.

This module provides the base DI container configuration using the dependency-injector
library. Application-specific containers (e.g., WebAPI) should extend this base container.

NOTE: This file is kept for backward compatibility. New code should use dependency-injector
containers defined in apps/webapi/di_container.py or similar application-specific containers.
"""

from dependency_injector import containers, providers
from typing import Optional

from libs.common.interfaces import IAppConfig, ILogger


class BaseContainer(containers.DeclarativeContainer):
    """Base dependency injection container.
    
    This container provides common services that can be shared across applications.
    Application-specific containers should extend this or create their own containers.
    """
    
    # Configuration will be provided by application-specific containers
    config: Optional[providers.Configuration] = providers.Configuration()
    
    # Logger will be provided by application-specific containers
    logger: Optional[providers.Singleton] = providers.Singleton(
        # This will be overridden by application containers
        lambda: None
    )

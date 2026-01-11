"""Dependency injection container (common implementation)."""

from typing import Any, Callable, Dict, Optional, Type, TypeVar

T = TypeVar("T")


class DIContainer:
    """Dependency injection container."""

    def __init__(self) -> None:
        """Initialize DI container."""
        self._services: Dict[Type[Any], Any] = {}
        self._factories: Dict[Type[Any], Callable[[], Any]] = {}
        self._singletons: Dict[Type[Any], Any] = {}

    def register_singleton(self, service_type: Type[T], instance: T) -> None:
        """Register a singleton instance."""
        self._singletons[service_type] = instance

    def register_transient(
        self, service_type: Type[T], factory: Callable[[], T]
    ) -> None:
        """Register a transient factory."""
        self._factories[service_type] = factory

    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """Register an instance (same as singleton)."""
        self.register_singleton(service_type, instance)

    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service instance."""
        # Check singletons first
        if service_type in self._singletons:
            return self._singletons[service_type]

        # Check factories
        if service_type in self._factories:
            return self._factories[service_type]()

        # Check direct registration
        if service_type in self._services:
            return self._services[service_type]

        raise ValueError(f"Service {service_type} is not registered")

    def is_registered(self, service_type: Type[Any]) -> bool:
        """Check if a service is registered."""
        return (
            service_type in self._singletons
            or service_type in self._factories
            or service_type in self._services
        )

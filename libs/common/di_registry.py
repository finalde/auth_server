"""DI registration utilities."""

from typing import Callable, Type, TypeVar

from libs.common.di_container import DIContainer

T = TypeVar("T")


def register_singleton(
    container: DIContainer, service_type: Type[T], instance: T
) -> None:
    """Register a singleton service."""
    container.register_singleton(service_type, instance)


def register_transient(
    container: DIContainer, service_type: Type[T], factory: Callable[[], T]
) -> None:
    """Register a transient service."""
    container.register_transient(service_type, factory)

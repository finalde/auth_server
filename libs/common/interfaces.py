"""Core interfaces for the application."""

from abc import ABC, abstractmethod
from typing import Any


class IAppConfig(ABC):
    """Application configuration interface."""

    @abstractmethod
    def get_database_url(self) -> str:
        """Get database connection URL."""
        pass


class ILogger(ABC):
    """Logger interface."""

    @abstractmethod
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        pass

    @abstractmethod
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        pass

    @abstractmethod
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        pass

    @abstractmethod
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        pass

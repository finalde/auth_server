"""Core interfaces for the application."""

from abc import ABC, abstractmethod
from typing import Any, List, Optional


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


class IClientReader(ABC):
    """Client reader interface."""

    @abstractmethod
    async def get_by_id_async(self, client_id: str) -> Any:
        """Get client by ID."""
        pass

    @abstractmethod
    async def get_all_async(self) -> List[Any]:
        """Get all clients."""
        pass


class IClientWriter(ABC):
    """Client writer interface."""

    @abstractmethod
    async def create_async(self, client: Any) -> Any:
        """Create client."""
        pass

    @abstractmethod
    async def update_async(self, client: Any) -> Any:
        """Update client."""
        pass

    @abstractmethod
    async def delete_async(self, client_id: str) -> None:
        """Delete client."""
        pass


class IUserReader(ABC):
    """User reader interface."""

    @abstractmethod
    async def get_by_id_async(self, user_id: str) -> Any:
        """Get user by ID."""
        pass

    @abstractmethod
    async def get_by_username_async(self, username: str) -> Any:
        """Get user by username."""
        pass

    @abstractmethod
    async def get_all_async(self) -> List[Any]:
        """Get all users."""
        pass


class IUserWriter(ABC):
    """User writer interface."""

    @abstractmethod
    async def create_async(self, user: Any) -> Any:
        """Create user."""
        pass

    @abstractmethod
    async def update_async(self, user: Any) -> Any:
        """Update user."""
        pass

    @abstractmethod
    async def delete_async(self, user_id: str) -> None:
        """Delete user."""
        pass


class IResourceReader(ABC):
    """Resource reader interface."""

    @abstractmethod
    async def get_by_id_async(self, resource_id: str) -> Any:
        """Get resource by ID."""
        pass

    @abstractmethod
    async def get_all_async(self) -> List[Any]:
        """Get all resources."""
        pass


class IResourceWriter(ABC):
    """Resource writer interface."""

    @abstractmethod
    async def create_async(self, resource: Any) -> Any:
        """Create resource."""
        pass

    @abstractmethod
    async def update_async(self, resource: Any) -> Any:
        """Update resource."""
        pass

    @abstractmethod
    async def delete_async(self, resource_id: str) -> None:
        """Delete resource."""
        pass


class IScopeReader(ABC):
    """Scope reader interface."""

    @abstractmethod
    async def get_by_name_async(self, scope_name: str) -> Any:
        """Get scope by name."""
        pass

    @abstractmethod
    async def get_all_async(self) -> List[Any]:
        """Get all scopes."""
        pass


class IScopeWriter(ABC):
    """Scope writer interface."""

    @abstractmethod
    async def create_async(self, scope: Any) -> Any:
        """Create scope."""
        pass

    @abstractmethod
    async def update_async(self, scope: Any) -> Any:
        """Update scope."""
        pass

    @abstractmethod
    async def delete_async(self, scope_name: str) -> None:
        """Delete scope."""
        pass

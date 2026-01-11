"""WebAPI configuration."""

from libs.common.interfaces import IAppConfig


class WebAPIConfig(IAppConfig):
    """WebAPI configuration implementation."""

    def __init__(self, database_url: str) -> None:
        """Initialize configuration."""
        self._database_url: str = database_url

    def get_database_url(self) -> str:
        """Get database connection URL."""
        return self._database_url

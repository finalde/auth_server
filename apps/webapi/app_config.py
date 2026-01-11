"""WebAPI configuration."""

import os
from typing import Optional

import yaml

from libs.common.interfaces import IAppConfig


class WebAPIConfig(IAppConfig):
    """WebAPI configuration implementation."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize configuration from YAML file."""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), "config.yml"
            )

        self._config_path: str = config_path
        self._config: dict = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                config: dict = yaml.safe_load(f) or {}
                return config
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file not found: {self._config_path}"
            )
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")

    def get_database_url(self) -> str:
        """Get database connection URL."""
        db_config: dict = self._config.get("database", {})
        host: str = db_config.get("host", "localhost")
        port: int = db_config.get("port", 5432)
        database: str = db_config.get("database", "auth_server")
        user: str = db_config.get("user", "postgres")
        password: str = db_config.get("password", "")

        # Allow environment variable override
        db_url: Optional[str] = os.getenv("DATABASE_URL")
        if db_url:
            return db_url

        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    def get_database_host(self) -> str:
        """Get database host."""
        return self._config.get("database", {}).get("host", "localhost")

    def get_database_port(self) -> int:
        """Get database port."""
        return self._config.get("database", {}).get("port", 5432)

    def get_database_name(self) -> str:
        """Get database name."""
        return self._config.get("database", {}).get("database", "auth_server")

    def get_database_user(self) -> str:
        """Get database user."""
        return self._config.get("database", {}).get("user", "postgres")

    def get_database_password(self) -> str:
        """Get database password."""
        return self._config.get("database", {}).get("password", "")

    def get_debug(self) -> bool:
        """Get debug flag."""
        return self._config.get("application", {}).get("debug", False)

    def get_log_level(self) -> str:
        """Get log level."""
        return self._config.get("application", {}).get("log_level", "INFO")

    def get_server_host(self) -> str:
        """Get server host."""
        return self._config.get("server", {}).get("host", "0.0.0.0")

    def get_server_port(self) -> int:
        """Get server port."""
        return self._config.get("server", {}).get("port", 8000)

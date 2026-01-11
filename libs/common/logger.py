"""Structured logging setup."""

import logging
import sys
from typing import Any, Optional

from libs.common.interfaces import ILogger


class Logger(ILogger):
    """Structured logger implementation."""

    def __init__(self, name: str, level: int = logging.INFO) -> None:
        """Initialize logger."""
        self._logger: logging.Logger = logging.getLogger(name)
        self._logger.setLevel(level)

        if not self._logger.handlers:
            handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
            formatter: logging.Formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self._logger.info(message, extra=kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self._logger.error(message, extra=kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._logger.warning(message, extra=kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._logger.debug(message, extra=kwargs)

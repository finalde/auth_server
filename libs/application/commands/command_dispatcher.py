"""Command dispatcher."""

from typing import Any, Dict, Type, TypeVar

from libs.common.interfaces import ILogger

TCommand = TypeVar("TCommand")
THandler = TypeVar("THandler")


class CommandDispatcher:
    """Command dispatcher for routing commands to handlers."""

    def __init__(self, logger: ILogger) -> None:
        """Initialize command dispatcher."""
        self._handlers: Dict[Type[Any], Any] = {}
        self._logger: ILogger = logger

    def register_handler(self, command_type: Type[TCommand], handler: Any) -> None:
        """Register a command handler."""
        self._handlers[command_type] = handler
        self._logger.debug(
            f"Registered handler for command type: {command_type.__name__}"
        )

    async def dispatch_async(self, command: TCommand) -> Any:
        """Dispatch command to appropriate handler."""
        command_type: Type[TCommand] = type(command)
        handler: Any = self._handlers.get(command_type)

        if not handler:
            raise ValueError(f"No handler registered for command type: {command_type.__name__}")

        self._logger.debug(f"Dispatching command: {command_type.__name__}")
        return await handler.handle_async(command)

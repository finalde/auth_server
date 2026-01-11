"""Scope entity."""

from dataclasses import dataclass


@dataclass
class Scope:
    """Scope domain entity."""

    scope_name: str
    description: str = ""
    is_active: bool = True

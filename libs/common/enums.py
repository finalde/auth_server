"""All enum definitions."""

from enum import Enum


class UserStatusEnum(str, Enum):
    """User status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class TokenTypeEnum(str, Enum):
    """Token type enumeration."""

    ACCESS = "access"
    REFRESH = "refresh"
    ID = "id"

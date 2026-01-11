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


class GrantTypeEnum(str, Enum):
    """OAuth2 grant type enumeration."""

    AUTHORIZATION_CODE = "authorization_code"
    IMPLICIT = "implicit"
    CLIENT_CREDENTIALS = "client_credentials"
    PASSWORD = "password"
    REFRESH_TOKEN = "refresh_token"


class ResponseTypeEnum(str, Enum):
    """OAuth2 response type enumeration."""

    CODE = "code"
    TOKEN = "token"
    ID_TOKEN = "id_token"

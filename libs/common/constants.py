"""Application-wide constants."""

# API Constants
API_VERSION: str = "v1"
API_PREFIX: str = f"/api/{API_VERSION}"

# Token Constants
ACCESS_TOKEN_EXPIRY_MINUTES: int = 15
REFRESH_TOKEN_EXPIRY_DAYS: int = 7

# Security Constants
PASSWORD_MIN_LENGTH: int = 8
PASSWORD_HASH_ALGORITHM: str = "bcrypt"

"""Route constants."""

from typing import Final

from fastapi import APIRouter

# Base routes
API_BASE: Final[str] = "/api/v1"
HEALTH: Final[str] = "/health"

# Auth routes (example)
AUTH_BASE: Final[str] = f"{API_BASE}/auth"
AUTH_LOGIN: Final[str] = f"{AUTH_BASE}/login"
AUTH_LOGOUT: Final[str] = f"{AUTH_BASE}/logout"

# Create router
router: APIRouter = APIRouter()

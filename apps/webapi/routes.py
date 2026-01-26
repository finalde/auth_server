"""Route constants."""

from typing import Final

from fastapi import APIRouter

# Base routes
API_BASE: Final[str] = "/api/v1"
HEALTH: Final[str] = "/health"

# Auth routes (OAuth2/OpenID Connect - handled by IdPyOIDC)
AUTH_BASE: Final[str] = f"{API_BASE}/auth"

# Management routes
CLIENTS_BASE: Final[str] = f"{API_BASE}/clients"
USERS_BASE: Final[str] = f"{API_BASE}/users"
RESOURCES_BASE: Final[str] = f"{API_BASE}/resources"
SCOPES_BASE: Final[str] = f"{API_BASE}/scopes"
USER_CLAIMS_BASE: Final[str] = f"{API_BASE}/user-claims"
USER_SCOPES_BASE: Final[str] = f"{API_BASE}/user-scopes"

# Create router
router: APIRouter = APIRouter()

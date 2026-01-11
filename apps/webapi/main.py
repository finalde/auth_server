"""FastAPI application entry point."""

from fastapi import FastAPI

from apps.webapi.controllers import auth__controller
from apps.webapi.routes import HEALTH, router

app: FastAPI = FastAPI(
    title="Auth Server API",
    description="OpenID Connect Provider API",
    version="1.0.0",
)

# Include routers
app.include_router(router)
app.include_router(auth__controller.router)


@app.get(HEALTH)
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

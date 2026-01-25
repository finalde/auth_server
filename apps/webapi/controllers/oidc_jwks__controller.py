"""OIDC JWKS endpoint controller."""

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from fastapi import Depends
from apps.webapi.dependencies import get_oidc_orchestration_service
from apps.webapi.routes import AUTH_BASE
from libs.application.services.oidc__orchestration_service import (
    OIDCOrchestrationService,
)

router: APIRouter = APIRouter(prefix=AUTH_BASE, tags=["oidc-jwks"])


@router.get("/jwks")
async def jwks_endpoint(
    request: Request,
    oidc_service: OIDCOrchestrationService = Depends(get_oidc_orchestration_service),
) -> JSONResponse:
    """JSON Web Key Set endpoint.
    
    Returns the JSON Web Key Set (JWKS) for token validation.
    JWKS spec: https://tools.ietf.org/html/rfc7517
    """
    try:
        server = oidc_service.get_oidc_server(request)
        endpoint_context = server.context
        jwks = endpoint_context.keyjar.export_jwks()
        return JSONResponse(content=jwks)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"JWKS error: {str(e)}"}
        )

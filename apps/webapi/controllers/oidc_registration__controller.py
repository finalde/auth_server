"""OIDC Dynamic Client Registration endpoint controller."""

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from fastapi import Depends
from apps.webapi.routes import AUTH_BASE
from libs.application.services.oidc__orchestration_service import (
    IOIDCOrchestrationService,
)
from apps.webapi.dependencies import get_oidc_orchestration_service

router: APIRouter = APIRouter(prefix=AUTH_BASE, tags=["oidc-registration"])


@router.post("/registration")
async def registration_endpoint(
    request: Request,
    oidc_service: IOIDCOrchestrationService = Depends(get_oidc_orchestration_service),
) -> JSONResponse:
    """Dynamic client registration endpoint.
    
    OIDC Dynamic Client Registration (OpenID Connect Registration 1.0).
    """
    try:
        server = oidc_service.get_oidc_server(request)
        endpoint = server.endpoint["registration"]

        body = await request.body()
        http_info = oidc_service.build_http_info(request)

        # Prepare request data
        request_data = body.decode("utf-8") if body else ""

        # Parse and process request
        parsed_request = endpoint.parse_request(request_data, http_info=http_info)
        response = endpoint.process_request(parsed_request)

        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"Registration error: {str(e)}"}
        )

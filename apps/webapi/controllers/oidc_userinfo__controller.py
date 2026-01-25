"""OIDC UserInfo endpoint controller."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from apps.webapi.dependencies import get_oidc_orchestration_service
from apps.webapi.routes import AUTH_BASE
from libs.application.services.oidc__orchestration_service import (
    IOIDCOrchestrationService,
)

router: APIRouter = APIRouter(prefix=AUTH_BASE, tags=["oidc-userinfo"])


@router.get("/userinfo")
@router.post("/userinfo")
async def userinfo_endpoint(
    request: Request,
    oidc_service: IOIDCOrchestrationService = Depends(get_oidc_orchestration_service),
) -> JSONResponse:
    """UserInfo endpoint for OpenID Connect user information.
    
    OIDC UserInfo Endpoint (OpenID Connect Core 1.0 Section 5.3).
    """
    try:
        server = oidc_service.get_oidc_server(request)
        endpoint = server.endpoint["userinfo"]

        body = await request.body() if request.method == "POST" else b""
        http_info = oidc_service.build_http_info(request)

        # Prepare request data
        if request.method == "GET":
            request_data = dict(request.query_params)
        else:
            request_data = body.decode("utf-8") if body else ""

        # Parse and process request
        parsed_request = endpoint.parse_request(request_data, http_info=http_info)
        response = endpoint.process_request(parsed_request)

        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"UserInfo error: {str(e)}"}
        )

"""OAuth2 token endpoint controller."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from fastapi import Depends
from apps.webapi.dependencies import get_oidc_token_orchestration_service
from apps.webapi.routes import AUTH_BASE
from libs.application.services.oidc_response__converter import (
    OIDCResponseConverter,
)
from libs.application.services.oidc_token__orchestration_service import (
    OIDCTokenOrchestrationService,
)

router: APIRouter = APIRouter(prefix=AUTH_BASE, tags=["oidc-token"])


@router.post("/token")
async def token_endpoint(
    request: Request,
    token_service: OIDCTokenOrchestrationService = Depends(
        get_oidc_token_orchestration_service
    ),
) -> JSONResponse:
    """Token endpoint for OAuth2 token exchange.
    
    OAuth2 Token Endpoint (RFC 6749 Section 3.2).
    """
    try:
        # Process token request
        result = await token_service.process_token_request(request)

        # Check for errors
        if "error" in result:
            error = result["error"]
            if isinstance(error, dict) and "error" in error:
                error_code = error.get("error", "invalid_request")
                if error_code in ["invalid_client", "invalid_grant", "unauthorized_client"]:
                    status_code = 401
                elif error_code == "server_error":
                    status_code = 500
                else:
                    status_code = 400
                return JSONResponse(status_code=status_code, content=error)

        # Convert response
        response = result.get("response")
        return OIDCResponseConverter.convert_token_response(response)
    except Exception as e:
        import traceback
        import logging

        logger = logging.getLogger(__name__)
        error_details = traceback.format_exc()
        logger.error(f"Token endpoint error: {error_details}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "server_error",
                "error_description": str(e),
                "error_type": type(e).__name__,
            },
        )

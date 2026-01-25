"""OAuth2 authorization endpoint controller."""

from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, Response

from fastapi import Depends
from apps.webapi.routes import AUTH_BASE
from libs.application.services.oidc_authorization__orchestration_service import (
    IOIDCAuthorizationOrchestrationService,
)
from libs.application.services.oidc_response__converter import (
    OIDCResponseConverter,
)
from apps.webapi.dependencies import get_oidc_authorization_orchestration_service

router: APIRouter = APIRouter(prefix=AUTH_BASE, tags=["oidc-authorization"])


@router.get("/authorization")
async def authorization_endpoint(
    request: Request,
    authorization_service: IOIDCAuthorizationOrchestrationService = Depends(
        get_oidc_authorization_orchestration_service
    ),
) -> Response:
    """Authorization endpoint for OAuth2 authorization code flow.
    
    OAuth2 Authorization Endpoint (RFC 6749 Section 4.1.1).
    """
    try:
        # Check if user is authenticated
        # TODO: Check session for authenticated user
        user = request.query_params.get("user")  # Temporary - use session in production

        if not user:
            # User not authenticated - redirect to login page
            # Get base URL from the orchestration service
            base_url = authorization_service.oidc_service.get_base_url(request)
            query_params = dict(request.query_params)
            query_string = "&".join(f"{k}={v}" for k, v in query_params.items())
            return RedirectResponse(
                url=f"{base_url}/api/v1/auth/login?{query_string}",
                status_code=302,
            )

        # Process authorization request
        result = authorization_service.process_authorization_request(request, user)
        response = result["response"]
        request_data = result["request_data"]

        # Convert IdPyOIDC response to FastAPI response
        return OIDCResponseConverter.convert_authorization_response(
            response, request_data
        )
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Authorization endpoint error: {str(e)}", exc_info=True)
        return Response(
            status_code=500,
            content=f"Authorization error: {str(e)}",
            media_type="text/plain",
        )

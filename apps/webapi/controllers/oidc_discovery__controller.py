"""OIDC Discovery endpoints controller."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from apps.webapi.dependencies import get_oidc_discovery_query_service
from libs.application.services.oidc_discovery__query_service import (
    OIDCDiscoveryQueryService,
)

# Well-known endpoints router (no prefix - must be at root level per OAuth2/OIDC spec)
# OIDC Discovery spec: https://openid.net/specs/openid-connect-discovery-1_0.html
router: APIRouter = APIRouter(tags=["oidc-discovery"])


@router.get("/.well-known/openid-configuration")
async def openid_configuration(
    request: Request,
    discovery_service: OIDCDiscoveryQueryService = Depends(
        get_oidc_discovery_query_service
    ),
) -> JSONResponse:
    """OpenID Connect discovery endpoint.
    
    Returns the OpenID Provider Configuration Document.
    OIDC Discovery spec: https://openid.net/specs/openid-connect-discovery-1_0.html
    """
    try:
        provider_info = discovery_service.get_openid_configuration(request)
        return JSONResponse(content=provider_info)
    except AttributeError as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Provider info not available: {str(e)}"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Configuration error: {str(e)}"},
        )


@router.get("/.well-known/oauth-authorization-server")
async def oauth_authorization_server(
    request: Request,
    discovery_service: OIDCDiscoveryQueryService = Depends(
        get_oidc_discovery_query_service
    ),
) -> JSONResponse:
    """OAuth2 Authorization Server Metadata endpoint.
    
    Returns OAuth2 Authorization Server Metadata (RFC 8414).
    """
    try:
        provider_info = discovery_service.get_oauth_authorization_server_metadata(request)
        return JSONResponse(content=provider_info)
    except AttributeError as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Provider info not available: {str(e)}"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Configuration error: {str(e)}"},
        )

"""Auth controller for OAuth2/OpenID Connect endpoints using IdPyOIDC."""

from typing import Any, Dict

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from apps.webapi.routes import AUTH_BASE

router: APIRouter = APIRouter(prefix=AUTH_BASE, tags=["auth"])

# Well-known endpoints router (no prefix - must be at root level per OAuth2/OIDC spec)
well_known_router: APIRouter = APIRouter(tags=["well-known"])


def _get_oidc_server(request: Request) -> Any:
    """Get OIDC server from request state."""
    if not hasattr(request.state, "oidc_server"):
        raise RuntimeError("OIDC server not initialized")
    return request.state.oidc_server


def _get_base_url(request: Request) -> str:
    """Get base URL from request, normalizing 0.0.0.0 to localhost."""
    base_url: str = str(request.base_url).rstrip("/")
    # Normalize 0.0.0.0 to localhost for issuer consistency
    if "0.0.0.0" in base_url:
        base_url = base_url.replace("0.0.0.0", "localhost")
    return base_url


@well_known_router.get("/.well-known/openid-configuration")
async def openid_configuration(request: Request) -> JSONResponse:
    """OpenID Connect discovery endpoint - handled by IdPyOIDC."""
    try:
        server: Any = _get_oidc_server(request)
        # IdPyOIDC Server has context attribute directly
        endpoint_context = server.context
        
        # Get base URL from request (must match discovery endpoint origin)
        base_url: str = _get_base_url(request)
        
        # Get provider info from endpoint context
        provider_info: Dict[str, Any] = endpoint_context.provider_info.copy()
        
        # Fix: Set issuer to match the discovery endpoint base URL (MUST rule)
        provider_info["issuer"] = base_url
        
        # Remove inline jwks if present (should not be in discovery doc)
        if "jwks" in provider_info:
            del provider_info["jwks"]
        
        # Add required jwks_uri pointing to the JWKS endpoint
        provider_info["jwks_uri"] = f"{base_url}/api/v1/auth/jwks"
        
        # Ensure ALL endpoints use the same base URL as issuer (MUST rule)
        provider_info["authorization_endpoint"] = f"{base_url}/api/v1/auth/authorization"
        provider_info["token_endpoint"] = f"{base_url}/api/v1/auth/token"
        provider_info["userinfo_endpoint"] = f"{base_url}/api/v1/auth/userinfo"
        
        # Fix: Ensure registration_endpoint uses same base URL, or remove if not needed
        if "registration_endpoint" in provider_info:
            provider_info["registration_endpoint"] = f"{base_url}/api/v1/auth/registration"
        # Alternative: Remove registration_endpoint if DCR is not supported
        # else:
        #     if "registration_endpoint" in provider_info:
        #         del provider_info["registration_endpoint"]
        
        return JSONResponse(content=provider_info)
    except AttributeError as e:
        # Handle case where provider_info might not be available yet
        return JSONResponse(
            status_code=500,
            content={"error": f"Provider info not available: {str(e)}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"Configuration error: {str(e)}"}
        )


@well_known_router.get("/.well-known/oauth-authorization-server")
async def oauth_authorization_server(request: Request) -> JSONResponse:
    """OAuth2 Authorization Server Metadata endpoint - handled by IdPyOIDC."""
    try:
        server: Any = _get_oidc_server(request)
        # IdPyOIDC Server has context attribute directly
        endpoint_context = server.context
        
        # Get base URL from request (must match discovery endpoint origin)
        base_url: str = _get_base_url(request)
        
        # Get provider info from endpoint context
        provider_info: Dict[str, Any] = endpoint_context.provider_info.copy()
        
        # Fix: Set issuer to match the discovery endpoint base URL
        provider_info["issuer"] = base_url
        
        # Remove inline jwks if present
        if "jwks" in provider_info:
            del provider_info["jwks"]
        
        # Add required jwks_uri
        provider_info["jwks_uri"] = f"{base_url}/api/v1/auth/jwks"
        
        # Ensure ALL endpoints use the same base URL as issuer
        provider_info["authorization_endpoint"] = f"{base_url}/api/v1/auth/authorization"
        provider_info["token_endpoint"] = f"{base_url}/api/v1/auth/token"
        if "userinfo_endpoint" in provider_info:
            provider_info["userinfo_endpoint"] = f"{base_url}/api/v1/auth/userinfo"
        
        # Fix: Ensure registration_endpoint uses same base URL, or remove if not needed
        if "registration_endpoint" in provider_info:
            provider_info["registration_endpoint"] = f"{base_url}/api/v1/auth/registration"
        # Alternative: Remove registration_endpoint if DCR is not supported
        # else:
        #     if "registration_endpoint" in provider_info:
        #         del provider_info["registration_endpoint"]
        
        return JSONResponse(content=provider_info)
    except AttributeError as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Provider info not available: {str(e)}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"Configuration error: {str(e)}"}
        )


@router.get("/authorization")
async def authorization_endpoint(request: Request) -> Response:
    """Authorization endpoint for OAuth2 authorization code flow - handled by IdPyOIDC."""
    try:
        server: Any = _get_oidc_server(request)
        # IdPyOIDC Server has endpoints as a dictionary attribute
        endpoint = server.endpoint["authorization"]
        
        # Prepare request data for IdPyOIDC
        body = await request.body() if request.method == "POST" else b""
        
        # IdPyOIDC processes requests - adapt based on actual API
        # Note: Actual implementation may need adjustment based on IdPyOIDC version
        response = endpoint.parse_request(
            request_info={
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "body": body.decode("utf-8") if body else "",
            }
        )
        
        # Process and return response
        resp = endpoint.process_request(response)
        
        if isinstance(resp, dict):
            return JSONResponse(content=resp)
        else:
            return Response(content=str(resp), media_type="text/html")
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"Authorization error: {str(e)}"}
        )


@router.post("/token")
async def token_endpoint(request: Request) -> JSONResponse:
    """Token endpoint for OAuth2 token exchange - handled by IdPyOIDC."""
    try:
        server: Any = _get_oidc_server(request)
        # IdPyOIDC Server has endpoints as a dictionary attribute
        endpoint = server.endpoint["token"]
        
        body = await request.body()
        form_data = await request.form()
        
        # Prepare request data for IdPyOIDC token endpoint
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "body": body.decode("utf-8") if body else "",
        }
        if form_data:
            request_info["form"] = dict(form_data)
        
        # Parse and process token request
        parsed_request = endpoint.parse_request(request_info)
        response = endpoint.process_request(parsed_request)
        
        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"Token error: {str(e)}"}
        )


@router.get("/userinfo")
@router.post("/userinfo")
async def userinfo_endpoint(request: Request) -> JSONResponse:
    """UserInfo endpoint for OpenID Connect user information - handled by IdPyOIDC."""
    try:
        server: Any = _get_oidc_server(request)
        # IdPyOIDC Server has endpoints as a dictionary attribute
        endpoint = server.endpoint["userinfo"]
        
        body = await request.body() if request.method == "POST" else b""
        
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "body": body.decode("utf-8") if body else "",
        }
        
        parsed_request = endpoint.parse_request(request_info)
        response = endpoint.process_request(parsed_request)
        
        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"UserInfo error: {str(e)}"}
        )


@router.get("/jwks")
async def jwks_endpoint(request: Request) -> JSONResponse:
    """JSON Web Key Set endpoint - handled by IdPyOIDC."""
    try:
        server: Any = _get_oidc_server(request)
        # IdPyOIDC Server has context attribute directly
        endpoint_context = server.context
        jwks = endpoint_context.keyjar.export_jwks()
        return JSONResponse(content=jwks)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"JWKS error: {str(e)}"}
        )


@router.post("/registration")
async def registration_endpoint(request: Request) -> JSONResponse:
    """Dynamic client registration endpoint - handled by IdPyOIDC."""
    try:
        server: Any = _get_oidc_server(request)
        # IdPyOIDC Server has endpoints as a dictionary attribute
        endpoint = server.endpoint["registration"]
        
        body = await request.body()
        
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "body": body.decode("utf-8") if body else "",
        }
        
        parsed_request = endpoint.parse_request(request_info)
        response = endpoint.process_request(parsed_request)
        
        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"Registration error: {str(e)}"}
        )

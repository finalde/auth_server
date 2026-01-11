"""Auth controller for OAuth2/OpenID Connect endpoints using IdPyOIDC."""

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from apps.webapi.routes import AUTH_BASE

router: APIRouter = APIRouter(prefix=AUTH_BASE, tags=["auth"])


def _get_oidc_server(request: Request) -> Any:
    """Get OIDC server from request state."""
    if not hasattr(request.state, "oidc_server"):
        raise RuntimeError("OIDC server not initialized")
    return request.state.oidc_server


@router.get("/.well-known/openid-configuration")
async def openid_configuration(request: Request) -> JSONResponse:
    """OpenID Connect discovery endpoint - handled by IdPyOIDC."""
    try:
        server: Any = _get_oidc_server(request)
        endpoint_context = server.server_get("endpoint_context")
        config: dict = endpoint_context.provider_info
        return JSONResponse(content=config)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"Configuration error: {str(e)}"}
        )


@router.get("/.well-known/oauth-authorization-server")
async def oauth_authorization_server(request: Request) -> JSONResponse:
    """OAuth2 Authorization Server Metadata endpoint - handled by IdPyOIDC."""
    try:
        server: Any = _get_oidc_server(request)
        endpoint_context = server.server_get("endpoint_context")
        config: dict = endpoint_context.provider_info
        return JSONResponse(content=config)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"Configuration error: {str(e)}"}
        )


@router.get("/authorization")
async def authorization_endpoint(request: Request) -> Response:
    """Authorization endpoint for OAuth2 authorization code flow - handled by IdPyOIDC."""
    try:
        server: Any = _get_oidc_server(request)
        endpoint = server.server_get("endpoint", "authorization")
        
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
        endpoint = server.server_get("endpoint", "token")
        
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
        endpoint = server.server_get("endpoint", "userinfo")
        
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
        endpoint_context = server.server_get("endpoint_context")
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
        endpoint = server.server_get("endpoint", "registration")
        
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

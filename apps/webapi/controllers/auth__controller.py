"""Auth controller for OAuth2/OpenID Connect endpoints using IdPyOIDC.

This module implements OAuth2/OIDC endpoints using IdPyOIDC library.
The implementation adapts IdPyOIDC for FastAPI/Starlette, as IdPyOIDC
documentation primarily shows Flask examples.

IdPyOIDC Documentation:
- Server setup: https://idpy-oidc.readthedocs.io/en/latest/server/contents/setup.html
- Configuration: https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html
- Session management: https://idpy-oidc.readthedocs.io/en/latest/server/contents/session_management.html
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse, Response, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path


from apps.webapi.routes import AUTH_BASE
router: APIRouter = APIRouter(prefix=AUTH_BASE, tags=["auth"])



# Well-known endpoints router (no prefix - must be at root level per OAuth2/OIDC spec)
# OIDC Discovery spec: https://openid.net/specs/openid-connect-discovery-1_0.html
well_known_router: APIRouter = APIRouter(tags=["well-known"])

# Templates for login page
# Use absolute path from project root
project_root = Path(__file__).parent.parent.parent.parent
templates = Jinja2Templates(directory=str(project_root / "apps" / "webapi" / "templates"))


def _get_oidc_server(request: Request) -> Any:
    """Get OIDC server from request state.

    The server is injected via middleware (see main.py OIDCMiddleware).
    IdPyOIDC Server structure: https://idpy-oidc.readthedocs.io/en/latest/server/contents/intro.html
    """
    if not hasattr(request.state, "oidc_server"):
        raise RuntimeError("OIDC server not initialized")
    return request.state.oidc_server


def _get_base_url(request: Request) -> str:
    """Get base URL from request, normalizing 0.0.0.0 to localhost.

    The issuer URL must match the discovery endpoint origin per OIDC Discovery spec.
    """
    base_url: str = str(request.base_url).rstrip("/")
    # Normalize 0.0.0.0 to localhost for issuer consistency
    if "0.0.0.0" in base_url:
        base_url = base_url.replace("0.0.0.0", "localhost")
    return base_url


def _build_http_info(request: Request) -> dict:
    """Build http_info dict for IdPyOIDC parse_request.
    
    IdPyOIDC parse_request expects http_info with:
    - headers: Request headers
    - url: Request URL
    - cookies: Request cookies (optional)
    """
    return {
        "headers": dict(request.headers),
        "url": str(request.url),
        "cookies": dict(request.cookies) if hasattr(request, "cookies") else {},
    }




@well_known_router.get("/.well-known/openid-configuration")
async def openid_configuration(request: Request) -> JSONResponse:
    """OpenID Connect discovery endpoint - handled by IdPyOIDC.

    Returns the OpenID Provider Configuration Document.
    OIDC Discovery spec: https://openid.net/specs/openid-connect-discovery-1_0.html

    The provider_info is retrieved from IdPyOIDC's endpoint context and then
    customized to ensure all endpoints use the same base URL as the issuer.
    """
    try:
        server: Any = _get_oidc_server(request)
        # IdPyOIDC Server has context attribute directly
        # Context provides access to provider_info and other server state
        endpoint_context = server.context
        
        # Get base URL from request (must match discovery endpoint origin)
        base_url: str = _get_base_url(request)
        
        # Get provider info from endpoint context
        # Provider info contains OIDC Discovery metadata
        # https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#capabilities
        provider_info: Dict[str, Any] = endpoint_context.provider_info.copy()
        
        # Fix: Set issuer to match the discovery endpoint base URL (MUST rule)
        provider_info["issuer"] = base_url
        
        # Remove inline jwks if present (should not be in discovery doc)
        # OIDC Discovery requires jwks_uri, not inline jwks
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
    """OAuth2 Authorization Server Metadata endpoint - handled by IdPyOIDC.

    Returns OAuth2 Authorization Server Metadata (RFC 8414).
    This endpoint typically returns similar information to the OIDC discovery endpoint.
    """
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


@router.get("/login")
async def login_page(
    request: Request,
    client_id: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    state: Optional[str] = None,
    scope: Optional[str] = None,
    response_type: Optional[str] = None,
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = None,
) -> HTMLResponse:
    """Login page for OAuth2 authorization flow.

    This is the login page that users see when redirected to the authorization endpoint.
    After authentication, the user will be redirected to complete the authorization flow.
    """
    # TODO: Look up client name from database
    client_name: Optional[str] = client_id
    
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "client_id": client_id,
            "client_name": client_name,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": scope,
            "response_type": response_type,
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method,
        },
    )


@router.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    client_id: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    scope: Optional[str] = Form(None),
    response_type: Optional[str] = Form("code"),
    code_challenge: Optional[str] = Form(None),
    code_challenge_method: Optional[str] = Form(None),
) -> Response:
    """Handle login form submission.

    After authentication, redirects to authorization endpoint to complete OAuth2 flow.
    """
    # TODO: Authenticate user against database
    # For now, simple validation (replace with real authentication)
    if not username or not password:
        # Redirect back to login with error
        params = {
            "error": "Username and password required",
        }
        if client_id:
            params["client_id"] = client_id
        if redirect_uri:
            params["redirect_uri"] = redirect_uri
        if state:
            params["state"] = state
        if scope:
            params["scope"] = scope
        
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return RedirectResponse(url=f"/api/v1/auth/login?{query_string}", status_code=302)
    
    # TODO: Validate credentials against user database
    # For now, accept any username/password (IMPLEMENT REAL AUTH)
    # In production, this should:
    # 1. Hash password and compare with stored hash
    # 2. Create session
    # 3. Store user ID in session
    
    # Build authorization URL with all parameters
    base_url: str = _get_base_url(request)
    auth_url = f"{base_url}/api/v1/auth/authorization"
    
    params: list[str] = []
    if client_id:
        params.append(f"client_id={client_id}")
    if redirect_uri:
        params.append(f"redirect_uri={redirect_uri}")
    if state:
        params.append(f"state={state}")
    if scope:
        params.append(f"scope={scope}")
    if response_type:
        params.append(f"response_type={response_type}")
    if code_challenge:
        params.append(f"code_challenge={code_challenge}")
    if code_challenge_method:
        params.append(f"code_challenge_method={code_challenge_method}")
    
    # Add user context (in production, this would come from session)
    # For now, we'll pass username as a parameter (not secure - use session)
    params.append(f"user={username}")  # TODO: Use session instead
    
    query_string = "&".join(params)
    return RedirectResponse(url=f"{auth_url}?{query_string}", status_code=302)


@router.get("/authorization")
async def authorization_endpoint(request: Request) -> Response:
    """Authorization endpoint for OAuth2 authorization code flow - handled by IdPyOIDC.

    OAuth2 Authorization Endpoint (RFC 6749 Section 4.1.1).
    IdPyOIDC endpoint: https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#authorization

    Note: FastAPI/Starlette integration adapts IdPyOIDC endpoints (which are designed
    primarily for Flask/WSGI) to work with ASGI. The request data is converted from
    Starlette Request to a format IdPyOIDC endpoints can process.
    """
    try:
        server: Any = _get_oidc_server(request)
        # IdPyOIDC Server has endpoints as a dictionary attribute
        # Access endpoint instances: https://idpy-oidc.readthedocs.io/en/latest/server/contents/intro.html
        endpoint = server.endpoint["authorization"]  
        # Check if user is authenticated
        # TODO: Check session for authenticated user
        user = request.query_params.get("user")  # Temporary - use session in production
        
        if not user:
            # User not authenticated - redirect to login page
            # Preserve all OAuth2 parameters
            query_params = dict(request.query_params)
            query_string = "&".join(f"{k}={v}" for k, v in query_params.items())
            base_url: str = _get_base_url(request)
            return RedirectResponse(
                url=f"{base_url}/api/v1/auth/login?{query_string}",
                status_code=302
            )
        
        # Prepare request data for IdPyOIDC
        # Prepare request data for IdPyOIDC
        # Authorization endpoint uses GET with query parameters
        # IdPyOIDC parse_request expects:
        # - request: dict (query params) or str (body)
        # - http_info: dict with headers, url, cookies
        request_data = dict(request.query_params)
        http_info = _build_http_info(request)
        
        # Parse request using IdPyOIDC endpoint
        parsed_request = endpoint.parse_request(request_data, http_info=http_info)
        
        # Process and return response
        resp = endpoint.process_request(parsed_request)
        
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
    """Token endpoint for OAuth2 token exchange - handled by IdPyOIDC.

    OAuth2 Token Endpoint (RFC 6749 Section 3.2).
    IdPyOIDC endpoint: https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#token
    """
    try:
        server: Any = _get_oidc_server(request)
        # IdPyOIDC Server has endpoints as a dictionary attribute
        endpoint = server.endpoint["token"]
        
        body = await request.body()
        form_data = await request.form()
        
        # Prepare request data for IdPyOIDC token endpoint
        # Token endpoint uses POST with form data
        # IdPyOIDC parse_request expects form data as dict
        request_data = dict(form_data) if form_data else {}
        http_info = _build_http_info(request)
        
        # Debug: Print request data
        print(f"Token request - client_id: {request_data.get('client_id')}, grant_type: {request_data.get('grant_type')}")
        
        # Parse and process token request
        try:
            parsed_request = endpoint.parse_request(request_data, http_info=http_info)
        except Exception as parse_error:
            print(f"Parse request error: {parse_error}")
            import traceback
            traceback.print_exc()
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_request",
                    "error_description": f"Failed to parse request: {str(parse_error)}"
                }
            )
        
        # Check if parse_request returned an error response
        if isinstance(parsed_request, dict) and "error" in parsed_request:
            print(f"Parse request returned error: {parsed_request}")
            return JSONResponse(
                status_code=400,
                content=parsed_request
            )
        
        try:
            response = endpoint.process_request(parsed_request)
        except Exception as process_error:
            # Check if this is an authentication/authorization error (should be 401/400, not 500)
            error_str = str(process_error).lower()
            error_type = type(process_error).__name__
            
            # Authentication errors (invalid_client, invalid_grant, etc.) should be 400/401
            if any(keyword in error_str for keyword in ['invalid_client', 'invalid_grant', 'invalid_secret', 
                                                         'unauthorized_client', 'authentication', 'credential']):
                status_code = 401
                error_code = "invalid_client"
            elif any(keyword in error_str for keyword in ['invalid_request', 'invalid_scope']):
                status_code = 400
                error_code = "invalid_request"
            else:
                # Unknown errors are server errors
                status_code = 500
                error_code = "server_error"
            
            print(f"Process request error ({error_code}): {process_error}")
            import traceback
            traceback.print_exc()
            
            return JSONResponse(
                status_code=status_code,
                content={
                    "error": error_code,
                    "error_description": str(process_error)
                }
            )
        
        # IdPyOIDC process_request returns a dict with response information
        # The response dict typically has 'response_args' key containing the actual response
        # or the response itself if it's already a dict
        if isinstance(response, dict):
            # Check if response has 'response_args' (common IdPyOIDC pattern)
            if 'response_args' in response:
                response_content = response['response_args']
            elif 'response' in response:
                response_content = response['response']
            else:
                response_content = response
        elif hasattr(response, 'to_dict'):
            response_content = response.to_dict()
        elif hasattr(response, '__dict__'):
            response_content = dict(response.__dict__)
        else:
            # Try to convert to dict
            try:
                if hasattr(response, 'response'):
                    response_content = response.response
                else:
                    response_content = {"response": str(response)}
            except:
                response_content = {"response": str(response)}
        
        # Ensure response_content is a dict
        if not isinstance(response_content, dict):
            response_content = {"response": str(response_content)}
        
        # Check if response contains an error
        if "error" in response_content:
            print(f"Process request returned error: {response_content}")
            error_code = response_content.get("error", "invalid_request")
            # Map OAuth2 error codes to HTTP status codes
            if error_code in ["invalid_client", "invalid_grant", "unauthorized_client"]:
                status_code = 401
            elif error_code == "server_error":
                status_code = 500
            else:
                status_code = 400  # invalid_request, invalid_scope, etc.
            return JSONResponse(
                status_code=status_code,
                content=response_content
            )
        
        return JSONResponse(content=response_content)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Token endpoint error: {error_details}")
        # Return more detailed error information
        error_response = {
            "error": "server_error",
            "error_description": str(e),
            "error_type": type(e).__name__,
        }
        # Include traceback in development (remove in production)
        if hasattr(request.app, "debug") and request.app.debug:
            error_response["traceback"] = error_details.split("\n")
        return JSONResponse(
            status_code=500, 
            content=error_response
        )


@router.get("/userinfo")
@router.post("/userinfo")
async def userinfo_endpoint(request: Request) -> JSONResponse:
    """UserInfo endpoint for OpenID Connect user information - handled by IdPyOIDC.

    OIDC UserInfo Endpoint (OpenID Connect Core 1.0 Section 5.3).
    IdPyOIDC endpoint: https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#userinfo
    """
    try:
        server: Any = _get_oidc_server(request)
        # IdPyOIDC Server has endpoints as a dictionary attribute
        endpoint = server.endpoint["userinfo"]
        
        body = await request.body() if request.method == "POST" else b""
        
        # Prepare request data for IdPyOIDC
        # UserInfo endpoint can use GET (query) or POST (body)
        if request.method == "GET":
            request_data = dict(request.query_params)
        else:
            # POST - use body as string
            request_data = body.decode("utf-8") if body else ""
        
        http_info = _build_http_info(request)
        
        parsed_request = endpoint.parse_request(request_data, http_info=http_info)
        response = endpoint.process_request(parsed_request)
        
        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"UserInfo error: {str(e)}"}
        )


@router.get("/jwks")
async def jwks_endpoint(request: Request) -> JSONResponse:
    """JSON Web Key Set endpoint - handled by IdPyOIDC.

    Returns the JSON Web Key Set (JWKS) for token validation.
    JWKS spec: https://tools.ietf.org/html/rfc7517

    The keyjar is accessed from the server's endpoint context.
    """
    try:
        server: Any = _get_oidc_server(request)
        # IdPyOIDC Server has context attribute directly
        # Keyjar contains signing keys: https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#keys
        endpoint_context = server.context
        jwks = endpoint_context.keyjar.export_jwks()
        return JSONResponse(content=jwks)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"JWKS error: {str(e)}"}
        )


@router.post("/registration")
async def registration_endpoint(request: Request) -> JSONResponse:
    """Dynamic client registration endpoint - handled by IdPyOIDC.

    OIDC Dynamic Client Registration (OpenID Connect Registration 1.0).
    IdPyOIDC endpoint: https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html#registration
    """
    try:
        server: Any = _get_oidc_server(request)
        # IdPyOIDC Server has endpoints as a dictionary attribute
        endpoint = server.endpoint["registration"]
        
        body = await request.body()
        
        # Prepare request data for IdPyOIDC
        # Registration endpoint uses POST with JSON body
        # IdPyOIDC parse_request expects body as string or dict
        request_data = body.decode("utf-8") if body else ""
        http_info = _build_http_info(request)
        
        parsed_request = endpoint.parse_request(request_data, http_info=http_info)
        response = endpoint.process_request(parsed_request)
        
        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"error": f"Registration error: {str(e)}"}
        )

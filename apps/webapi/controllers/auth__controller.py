"""Auth controller for OAuth2/OpenID Connect endpoints using IdPyOIDC.

This module implements OAuth2/OIDC endpoints using IdPyOIDC library.
The implementation adapts IdPyOIDC for FastAPI/Starlette, as IdPyOIDC
documentation primarily shows Flask examples.

IdPyOIDC Documentation:
- Server setup: https://idpy-oidc.readthedocs.io/en/latest/server/contents/setup.html
- Configuration: https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html
- Session management: https://idpy-oidc.readthedocs.io/en/latest/server/contents/session_management.html
"""

from typing import Any, Dict, Optional, Set

import json
from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse, Response, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from apps.webapi.routes import AUTH_BASE
router: APIRouter = APIRouter(prefix=AUTH_BASE, tags=["auth"])



# Well-known endpoints router (no prefix - must be at root level per OAuth2/OIDC spec)
# OIDC Discovery spec: https://openid.net/specs/openid-connect-discovery-1_0.html
well_known_router: APIRouter = APIRouter(tags=["well-known"])

_user_scopes_engine: Optional[Engine] = None


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


def _get_user_scopes(username: str) -> Set[str]:
    """Load active scopes for a given user from user_scopes table.

    This constrains which scopes a user is allowed to receive in tokens.
    """
    from apps.webapi.dependencies import get_config

    global _user_scopes_engine
    if _user_scopes_engine is None:
        db_url = get_config().get_database_url()
        _user_scopes_engine = create_engine(db_url, pool_pre_ping=True)

    scopes: Set[str] = set()
    with _user_scopes_engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT us.scope_name
                FROM user_scopes us
                JOIN users u ON u.user_id = us.user_id
                WHERE u.username = :username
                  AND us.is_active = TRUE
                """
            ),
            {"username": username},
        )
        for row in result:
            scopes.add(row.scope_name)
    return scopes


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
        # Authorization endpoint uses GET with query parameters
        # IdPyOIDC parse_request expects:
        # - request: dict (query params) or str (body)
        # - http_info: dict with headers, url, cookies
        request_data = dict(request.query_params)
        
        # IdPyOIDC may expect response_mode parameter (defaults to "query" for authorization code)
        # If not provided, set default to avoid KeyError
        if "response_mode" not in request_data:
            request_data["response_mode"] = "query"

        # Apply per-user scope filtering (user_scopes) BEFORE calling IdPyOIDC.
        # Effective scopes = requested ∩ client_allowed ∩ user_allowed.
        client_id = request_data.get("client_id")
        requested_scope_str = request_data.get("scope", "") or ""
        requested_scopes = requested_scope_str.split() if requested_scope_str else []

        # Load user-allowed scopes (may be empty if not configured)
        user_scopes = _get_user_scopes(user) if user else set()

        # Load client-allowed scopes from CDB
        client_allowed_scopes: list[str] = []
        if client_id:
            ctx = server.context
            try:
                client_info = ctx.cdb[client_id]
                if isinstance(client_info, dict):
                    client_allowed_scopes = client_info.get("scopes", []) or []
                else:
                    client_allowed_scopes = getattr(client_info, "scopes", []) or []
            except KeyError:
                client_allowed_scopes = []

        # Always allow 'openid' (OIDC user identity) if requested and client allows it
        always_allowed = {"openid"}
        effective_scopes: list[str] = []
        for s in requested_scopes:
            if s in always_allowed:
                if not client_allowed_scopes or s in client_allowed_scopes:
                    effective_scopes.append(s)
            else:
                if client_allowed_scopes and s not in client_allowed_scopes:
                    continue
                if user_scopes and s not in user_scopes:
                    continue
                effective_scopes.append(s)

        # If we computed a filtered scope list, update request_data
        if effective_scopes:
            request_data["scope"] = " ".join(effective_scopes)

        # Debug logging to show end-to-end scope filtering before IdPyOIDC
        # This helps verify that requested scopes and per-user scopes are correct,
        # and that any missing scopes in the final access token are due to IdPyOIDC.
        print(
            "Authorization endpoint scope debug:",
            {
                "user": user,
                "client_id": client_id,
                "requested_scopes": requested_scopes,
                "user_scopes": sorted(list(user_scopes)) if user_scopes else [],
                "client_allowed_scopes": client_allowed_scopes,
                "effective_scopes": effective_scopes,
                "request_data.scope": request_data.get("scope"),
            },
        )
        
        http_info = _build_http_info(request)
        
        # Scope filtering is handled by IdPyOIDC based on:
        # 1. Client's allowed scopes (from oauth2_clients.scopes via CDB)
        # 2. Requested scopes in the authorization request
        # IdPyOIDC automatically filters requested scopes to only include
        # scopes that the client is allowed to request (from client metadata)
        # 
        # For user-specific scope restrictions, implement by:
        # - Adding user_scopes table or user metadata for user permissions
        # - Querying user permissions from database
        # - Filtering scopes based on user + client permissions
        # This should be done here before calling IdPyOIDC, if needed
        
        # Parse request using IdPyOIDC endpoint
        print("=" * 80)
        print("🔍 About to call IdPyOIDC parse_request")
        print(f"request_data.scope: {request_data.get('scope')}")
        print(f"request_data keys: {list(request_data.keys())}")
        
        parsed_request = endpoint.parse_request(request_data, http_info=http_info)
        
        print(f"parsed_request type: {type(parsed_request)}")
        if isinstance(parsed_request, dict):
            print(f"parsed_request.scope: {parsed_request.get('scope')}")
        elif hasattr(parsed_request, 'scope'):
            print(f"parsed_request.scope (attr): {getattr(parsed_request, 'scope', 'N/A')}")
        
        # Process and return response
        # IdPyOIDC process_request may return:
        # - dict: JSON response (error cases)
        # - Response object: HTTP response (redirects, HTML forms, etc.)
        # - Message object (like AuthorizationErrorResponse): Needs to be converted
        print("About to call IdPyOIDC process_request (our patch should intercept)")
        resp = endpoint.process_request(parsed_request)
        print(f"process_request returned type: {type(resp)}")
        
        # Handle different response types from IdPyOIDC
        # IMPORTANT: Check for Message objects FIRST (they may be dict-like)
        # AuthorizationErrorResponse and other Message objects may inherit from dict
        # but are not JSON serializable directly - they need conversion
        # Check by class name to catch IdPyOIDC Message types
        resp_class_name = type(resp).__name__
        resp_type = type(resp)
        
        # Check if it's a dict subclass (not a plain dict) - these are likely IdPyOIDC Message objects
        # Dict subclasses can't be JSON serialized directly - they need conversion
        is_dict_subclass = isinstance(resp, dict) and resp_type is not dict
        
        # Check if class name suggests it's an IdPyOIDC Message (Response, ErrorResponse, etc.)
        is_likely_message = (
            'Response' in resp_class_name or 
            'ErrorResponse' in resp_class_name or
            'AuthorizationResponse' in resp_class_name
        )
        
        # CRITICAL: If it's a dict subclass OR has Response in name, it needs special handling
        # This catches AuthorizationErrorResponse and similar IdPyOIDC Message objects
        needs_conversion = is_dict_subclass or is_likely_message
        
        # Try to convert IdPyOIDC Message objects to dict
        if hasattr(resp, 'to_dict'):
            # Handle Message objects (like AuthorizationErrorResponse, AuthorizationResponse, etc.)
            # IdPyOIDC Message objects have to_dict() method
            resp_dict = resp.to_dict()
            # If it's an error response, we should redirect with error parameters
            if "error" in resp_dict:
                # Log detailed error for debugging
                print(f"Authorization endpoint error (to_dict): {resp_dict}")
                # Extract redirect_uri and state from original request
                redirect_uri = request_data.get("redirect_uri")
                state = request_data.get("state")
                if redirect_uri:
                    # Build error redirect URL per OAuth2 spec (RFC 6749 Section 4.1.2.1)
                    from urllib.parse import urlencode
                    error_params = {"error": resp_dict.get("error")}
                    if "error_description" in resp_dict:
                        error_params["error_description"] = resp_dict["error_description"]
                    if state:
                        error_params["state"] = state
                    redirect_url = f"{redirect_uri}?{urlencode(error_params)}"
                    return RedirectResponse(url=redirect_url, status_code=302)
                # If no redirect_uri, return JSON error
                return JSONResponse(
                    status_code=400,
                    content=resp_dict
                )
            # Non-error response - should be a success redirect with code
            redirect_uri = request_data.get("redirect_uri")
            if redirect_uri and "code" in resp_dict:
                from urllib.parse import urlencode
                success_params = {"code": resp_dict["code"]}
                if "state" in resp_dict:
                    success_params["state"] = resp_dict["state"]
                redirect_url = f"{redirect_uri}?{urlencode(success_params)}"
                return RedirectResponse(url=redirect_url, status_code=302)
            # Fallback: return as JSON
            return JSONResponse(content=resp_dict)
        elif needs_conversion:
            # IdPyOIDC Message type that's dict-like but not JSON serializable
            # Try to convert via __dict__ or manual conversion
            resp_dict = None
            try:
                # Try to_dict() first (might exist but not detected by hasattr)
                if hasattr(type(resp), 'to_dict') or hasattr(resp, 'to_dict'):
                    try:
                        resp_dict = resp.to_dict()
                    except (AttributeError, TypeError):
                        pass
                
                # If to_dict() didn't work, try converting from dict directly
                if resp_dict is None and isinstance(resp, dict):
                    # For dict subclasses, use dict() constructor or dict comprehension
                    # This creates a plain dict from the subclass
                    try:
                        resp_dict = {k: v for k, v in resp.items()}
                    except (AttributeError, TypeError):
                        # Fallback: try direct dict() constructor
                        try:
                            resp_dict = dict(resp)
                        except (TypeError, ValueError):
                            pass
                
                # If still None, try __dict__
                if resp_dict is None and hasattr(resp, '__dict__'):
                    resp_dict = {k: v for k, v in resp.__dict__.items() if not k.startswith('_')}
                
                # If still None, try to get common Message attributes directly
                if resp_dict is None:
                    resp_dict = {}
                    for key in ['error', 'error_description', 'error_uri', 'state', 'code']:
                        if hasattr(resp, key):
                            value = getattr(resp, key)
                            if value is not None:
                                resp_dict[key] = value
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to convert {resp_class_name} to dict: {e}")
                resp_dict = {"error": "server_error", "error_description": str(e)}
            
            # Handle error response
            if "error" in resp_dict:
                # Log detailed error for debugging
                print(f"Authorization endpoint error (needs_conversion): {resp_dict}")
                redirect_uri = request_data.get("redirect_uri")
                if redirect_uri:
                    from urllib.parse import urlencode
                    error_params = {"error": resp_dict.get("error")}
                    if "error_description" in resp_dict:
                        error_params["error_description"] = resp_dict["error_description"]
                    if request_data.get("state"):
                        error_params["state"] = request_data["state"]
                    redirect_url = f"{redirect_uri}?{urlencode(error_params)}"
                    return RedirectResponse(url=redirect_uri if '?' not in redirect_uri else redirect_url, status_code=302)
                return JSONResponse(status_code=400, content=resp_dict)
            # Handle success response
            redirect_uri = request_data.get("redirect_uri")
            if redirect_uri and "code" in resp_dict:
                from urllib.parse import urlencode
                success_params = {"code": resp_dict["code"]}
                if "state" in resp_dict:
                    success_params["state"] = resp_dict["state"]
                redirect_url = f"{redirect_uri}?{urlencode(success_params)}"
                return RedirectResponse(url=redirect_url, status_code=302)
            return JSONResponse(content=resp_dict)
        elif isinstance(resp, dict) and "response_args" in resp and "return_uri" in resp:
            # IdPyOIDC authorization endpoint often returns a dict:
            # { "response_args": <AuthorizationResponse|AuthorizationErrorResponse>, "return_uri": "<redirect_uri>" }
            # This is the canonical structure we should turn into an HTTP redirect for the SPA.
            response_args = resp.get("response_args")
            return_uri = resp.get("return_uri")

            # Convert response_args (Message or dict) to a simple dict
            args_dict: Dict[str, Any]
            if hasattr(response_args, "to_dict"):
                args_dict = response_args.to_dict()  # type: ignore[assignment]
            elif isinstance(response_args, dict):
                args_dict = dict(response_args)
            else:
                # Fallback: best-effort conversion
                try:
                    args_dict = {k: v for k, v in response_args.items()}  # type: ignore[attr-defined]
                except Exception:
                    args_dict = {"response": str(response_args)}

            # Build redirect URL with query parameters (code/state or error/error_description)
            from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse

            parsed = urlparse(return_uri)
            existing_qs = dict(parse_qsl(parsed.query))
            merged_qs = {**existing_qs, **args_dict}
            new_query = urlencode(merged_qs)
            new_url = urlunparse(parsed._replace(query=new_query))

            return RedirectResponse(url=new_url, status_code=302)
        elif isinstance(resp, dict):
            # Any other dict (plain or subclass) - convert to a plain dict first.
            # If JSON serialization still fails, fall back to a plain text response.
            try:
                plain_dict = {k: v for k, v in resp.items()}
            except Exception:
                plain_dict = dict(resp)

            try:
                json.dumps(plain_dict)
                return JSONResponse(content=plain_dict)
            except TypeError:
                return Response(content=str(plain_dict), media_type="text/plain")
        elif hasattr(resp, 'status_code') and hasattr(resp, 'headers'):
            # IdPyOIDC Response object - check if it's a redirect
            if resp.status_code in (302, 303, 307, 308):
                # Extract redirect URL from Location header
                location = resp.headers.get("Location")
                if location:
                    return RedirectResponse(url=location, status_code=resp.status_code)
            # Return as-is for other response types
            return Response(
                content=resp.message if hasattr(resp, 'message') else str(resp),
                status_code=resp.status_code,
                headers=dict(resp.headers),
                media_type=resp.headers.get("Content-Type", "text/html")
            )
        elif hasattr(resp, '__dict__'):
            # Try to convert via __dict__ (less reliable, but fallback for objects without to_dict())
            resp_dict = {k: v for k, v in resp.__dict__.items() if not k.startswith('_')}
            # Check if it's an error response
            if "error" in resp_dict:
                redirect_uri = request_data.get("redirect_uri")
                if redirect_uri:
                    from urllib.parse import urlencode
                    error_params = {"error": resp_dict.get("error")}
                    if "error_description" in resp_dict:
                        error_params["error_description"] = resp_dict["error_description"]
                    if request_data.get("state"):
                        error_params["state"] = request_data["state"]
                    redirect_url = f"{redirect_uri}?{urlencode(error_params)}"
                    return RedirectResponse(url=redirect_url, status_code=302)
                return JSONResponse(content=resp_dict)
            # Non-error - check if it has code for success redirect
            redirect_uri = request_data.get("redirect_uri")
            if redirect_uri and "code" in resp_dict:
                from urllib.parse import urlencode
                success_params = {"code": resp_dict["code"]}
                if "state" in resp_dict:
                    success_params["state"] = resp_dict["state"]
                redirect_url = f"{redirect_uri}?{urlencode(success_params)}"
                return RedirectResponse(url=redirect_url, status_code=302)
            return JSONResponse(content=resp_dict)
        else:
            # Fallback: convert to string response
            return Response(content=str(resp), media_type="text/html")
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Authorization endpoint error: {str(e)}", exc_info=True)
        # Return more detailed error for debugging (remove in production)
        return JSONResponse(
            status_code=500, 
            content={
                "error": f"Authorization error: {str(e)}",
                "error_type": type(e).__name__,
            }
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
        
        # Debug: Print request data (don't log secrets)
        client_id = request_data.get('client_id')
        grant_type = request_data.get('grant_type')
        print(f"Token request - client_id: {client_id}, grant_type: {grant_type}")
        
        # Parse and process token request
        try:
            parsed_request = endpoint.parse_request(request_data, http_info=http_info)
        except Exception as parse_error:
            # Log parse errors with more context
            error_msg = str(parse_error)
            print(f"Parse request error: {error_msg}")
            # Only print full traceback for unexpected errors, not authentication failures
            if "client" not in error_msg.lower() and "secret" not in error_msg.lower() and "auth" not in error_msg.lower():
                import traceback
                traceback.print_exc()
            
            # Return appropriate error response
            if "client" in error_msg.lower() or "secret" in error_msg.lower() or "auth" in error_msg.lower():
                return JSONResponse(
                    status_code=401,
                    content={
                        "error": "invalid_client",
                        "error_description": "Client authentication failed"
                    }
                )
            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_request",
                    "error_description": f"Failed to parse request: {error_msg}"
                }
            )
        
        # Check if parse_request returned an error response
        if isinstance(parsed_request, dict) and "error" in parsed_request:
            print(f"Parse request returned error: {parsed_request}")
            error_code = parsed_request.get("error", "invalid_request")
            # Map OAuth2 error codes to HTTP status codes
            if error_code in ["invalid_client", "invalid_grant", "unauthorized_client"]:
                status_code = 401
            elif error_code == "server_error":
                status_code = 500
            else:
                status_code = 400
            return JSONResponse(
                status_code=status_code,
                content=parsed_request
            )
        
        try:
            response = endpoint.process_request(parsed_request)
        except KeyError as key_error:
            # KeyError usually means missing required field (like client_id)
            # This typically indicates authentication failure
            missing_key = str(key_error)
            print(f"Process request error - missing key: {missing_key}")
            
            if "client_id" in missing_key:
                return JSONResponse(
                    status_code=401,
                    content={
                        "error": "invalid_client",
                        "error_description": "Client authentication failed: missing client_id"
                    }
                )
            else:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "invalid_request",
                        "error_description": f"Missing required parameter: {missing_key}"
                    }
                )
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
                # Unknown errors are server errors - log full traceback for debugging
                status_code = 500
                error_code = "server_error"
                import traceback
                print(f"Process request error ({error_code}): {process_error}")
                traceback.print_exc()
            
            if status_code != 500:
                # For expected errors, just log the error message
                print(f"Process request error ({error_code}): {process_error}")
            
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

        # Debug: log token response content and scope for diagnostics
        print(
            "Token endpoint response debug:",
            {
                "keys": list(response_content.keys()),
                "scope": response_content.get("scope"),
                "error": response_content.get("error"),
                "error_description": response_content.get("error_description"),
            },
        )
        
        # Decode and print the actual scope in the access token JWT
        if "access_token" in response_content and not response_content.get("error"):
            try:
                import base64
                import json
                access_token = response_content.get("access_token")
                if access_token:
                    # Decode JWT payload (second part)
                    parts = access_token.split(".")
                    if len(parts) >= 2:
                        payload_part = parts[1]
                        # Add padding if needed
                        padding = 4 - len(payload_part) % 4
                        if padding != 4:
                            payload_part += "=" * padding
                        decoded_payload = base64.urlsafe_b64decode(payload_part)
                        token_payload = json.loads(decoded_payload)
                        
                        # Print the scope that's actually in the token
                        scope_in_token = token_payload.get("scope", "NOT FOUND")
                        scope_list = scope_in_token.split() if isinstance(scope_in_token, str) else scope_in_token
                        
                        print("=" * 80)
                        print("🔐 FINAL TOKEN SCOPE - What scope is actually granted in the access token:")
                        print("=" * 80)
                        print(f"Scope in token: {scope_in_token}")
                        print(f"Scope list: {scope_list}")
                        print(f"Has 'openid': {'openid' in scope_list}")
                        print(f"Has 'data.read': {'data.read' in scope_list}")
                        print(f"Has 'data.write': {'data.write' in scope_list}")
                        print(f"Has 'read': {'read' in scope_list}")
                        print(f"Has 'write': {'write' in scope_list}")
                        print(f"Has 'admin': {'admin' in scope_list}")
                        print("=" * 80)
            except Exception as e:
                print(f"Warning: Could not decode access token to check scope: {e}")

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

        # If no error and no scope is present, log an explicit warning – likely an IdPyOIDC issue
        if "scope" not in response_content:
            print(
                "WARNING: Token issued without 'scope' claim in response_content. "
                "Requested scopes were handled in authorization endpoint; "
                "missing scope here indicates IdPyOIDC did not add scope to the access token."
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

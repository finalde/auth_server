"""OAuth2 login page controller."""

from typing import Optional

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from fastapi import Depends
from apps.webapi.dependencies import get_oidc_orchestration_service, get_user_auth_service
from apps.webapi.routes import AUTH_BASE
from libs.application.services.oidc__orchestration_service import (
    OIDCOrchestrationService,
)
from libs.application.services.user_auth__service import UserAuthService

router: APIRouter = APIRouter(prefix=AUTH_BASE, tags=["auth-login"])

# Templates for login page
project_root = Path(__file__).parent.parent.parent.parent
templates = Jinja2Templates(
    directory=str(project_root / "apps" / "webapi" / "templates")
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
    """Login page for OAuth2 authorization flow."""
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
    oidc_service: OIDCOrchestrationService = Depends(get_oidc_orchestration_service),
    auth_service: UserAuthService = Depends(get_user_auth_service),
) -> RedirectResponse:
    """Handle login form submission."""
    if not username or not password:
        params = {"error": "Username and password required"}
        if client_id:
            params["client_id"] = client_id
        if redirect_uri:
            params["redirect_uri"] = redirect_uri
        if state:
            params["state"] = state
        if scope:
            params["scope"] = scope

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return RedirectResponse(
            url=f"/api/v1/auth/login?{query_string}", status_code=302
        )

    is_valid = await auth_service.authenticate_async(username=username, password=password)
    if not is_valid:
        params = {"error": "Invalid username or password"}
        if client_id:
            params["client_id"] = client_id
        if redirect_uri:
            params["redirect_uri"] = redirect_uri
        if state:
            params["state"] = state
        if scope:
            params["scope"] = scope

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return RedirectResponse(
            url=f"/api/v1/auth/login?{query_string}", status_code=302
        )

    # Build authorization URL
    base_url = oidc_service.get_base_url(request) if oidc_service else str(request.base_url).rstrip("/")
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
    params.append(f"user={username}")  # TODO: Use session instead

    query_string = "&".join(params)
    return RedirectResponse(url=f"{auth_url}?{query_string}", status_code=302)

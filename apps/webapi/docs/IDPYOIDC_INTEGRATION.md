# IdPyOIDC FastAPI Integration Guide

This document describes how IdPyOIDC is integrated with FastAPI in this project. Since IdPyOIDC documentation primarily shows Flask/WSGI examples, this guide explains our FastAPI/ASGI adaptation.

## Overview

IdPyOIDC is a Python library for implementing OAuth2 and OpenID Connect providers. The official documentation shows Flask examples, but IdPyOIDC can be adapted for FastAPI/Starlette (ASGI) applications.

**IdPyOIDC Documentation**: https://idpy-oidc.readthedocs.io/en/latest/index.html

## Architecture

### Server Initialization

The IdPyOIDC server is initialized as a singleton using the `OIDCServerService` class:

```python
from libs.infrastructure.services.oidc_server_service import OIDCServerService

oidc_service = OIDCServerService(issuer="http://localhost:8000")
oidc_service.configure({})
server = oidc_service.get_server()
```

**Configuration Structure**: Follows IdPyOIDC documentation patterns:
- https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html
- https://idpy-oidc.readthedocs.io/en/latest/server/contents/setup.html

### Server Lifecycle

The server is initialized once at application startup and stored in `app.state`:

```python
@app.on_event("startup")
async def startup_event():
    oidc_service = OIDCServerService(issuer=base_url)
    oidc_service.configure({})
    app.state.oidc_server_service = oidc_service
```

Middleware injects the server instance into each request's state:

```python
class OIDCMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.oidc_server = request.app.state.oidc_server_service.get_server()
        response = await call_next(request)
        return response
```

## Endpoint Handling

### Accessing Server and Endpoints

IdPyOIDC Server provides access to:
- `server.context` - Endpoint context (provider_info, keyjar, etc.)
- `server.endpoint` - Dictionary of endpoint instances

```python
server = request.state.oidc_server
endpoint_context = server.context
authorization_endpoint = server.endpoint["authorization"]
```

### Request Processing

Unlike Flask examples in IdPyOIDC docs, FastAPI endpoints must:
1. Convert Starlette `Request` to format IdPyOIDC expects
2. Call IdPyOIDC endpoint methods (`parse_request`, `process_request`)
3. Convert IdPyOIDC response to FastAPI/Starlette `Response`

**Example Pattern**:

```python
@router.post("/token")
async def token_endpoint(request: Request) -> JSONResponse:
    server = _get_oidc_server(request)
    endpoint = server.endpoint["token"]
    
    # Convert Starlette Request to dict format
    body = await request.body()
    form_data = await request.form()
    
    request_info = {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "body": body.decode("utf-8") if body else "",
    }
    if form_data:
        request_info["form"] = dict(form_data)
    
    # Process with IdPyOIDC
    parsed_request = endpoint.parse_request(request_info)
    response = endpoint.process_request(parsed_request)
    
    # Return FastAPI response
    return JSONResponse(content=response)
```

## Discovery Endpoints

### Well-Known Endpoints

OIDC Discovery requires well-known endpoints at the root level:
- `/.well-known/openid-configuration`
- `/.well-known/oauth-authorization-server`

These are implemented using a separate router without prefix:

```python
well_known_router = APIRouter(tags=["well-known"])

@well_known_router.get("/.well-known/openid-configuration")
async def openid_configuration(request: Request) -> JSONResponse:
    server = _get_oidc_server(request)
    endpoint_context = server.context
    provider_info = endpoint_context.provider_info.copy()
    
    # Customize provider_info to ensure valid OIDC discovery document
    # (fix issuer, jwks_uri, endpoint URLs)
    
    return JSONResponse(content=provider_info)
```

### Provider Info Customization

The IdPyOIDC-generated `provider_info` is customized to ensure:
1. **Issuer matches discovery endpoint origin** (OIDC Discovery MUST rule)
2. **All endpoints use same base URL** (OIDC Discovery MUST rule)
3. **jwks_uri is present** (no inline jwks)

## Configuration

### Configuration Structure

Configuration follows IdPyOIDC patterns documented at:
https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html

Key sections:
- `issuer` - OP issuer URI
- `keys` - Key definitions for signing
- `token_handler_args` - Token handler configuration
- `endpoint` - Endpoint paths and classes
- `session_params` - Session management
- Discovery capabilities (`response_types_supported`, etc.)

### Endpoint Configuration

Endpoints are configured with:
- `path` - Relative path (combined with issuer for full URL)
- `class` - IdPyOIDC endpoint class
- `kwargs` - Endpoint-specific arguments

Example:
```python
"endpoint": {
    "authorization": {
        "path": "authorization",
        "class": "idpyoidc.server.oidc.authorization.Authorization",
        "kwargs": {},
    },
    "token": {
        "path": "token",
        "class": "idpyoidc.server.oidc.token.Token",
        "kwargs": {},
    },
}
```

## Differences from Flask Examples

### 1. Request/Response Handling

**Flask (WSGI)**:
- IdPyOIDC endpoints can work directly with Flask request objects
- Flask's WSGI environment maps naturally to IdPyOIDC's expectations

**FastAPI (ASGI)**:
- Starlette `Request` objects need conversion to dict/HTTPRequest format
- Response objects need to be created from IdPyOIDC return values

### 2. Async/Await

**Flask**:
- Synchronous request handling
- IdPyOIDC methods are called directly

**FastAPI**:
- Async request handling
- IdPyOIDC methods are called within async functions
- Request body/form data must be awaited

### 3. Server Access

**Flask**:
- Server can be stored in Flask app context or global variable

**FastAPI**:
- Server stored in `app.state` (application state)
- Injected into request state via middleware
- Accessed via `request.state.oidc_server`

## References

### IdPyOIDC Documentation

- **Main Documentation**: https://idpy-oidc.readthedocs.io/en/latest/index.html
- **Server Setup**: https://idpy-oidc.readthedocs.io/en/latest/server/contents/setup.html
- **Configuration**: https://idpy-oidc.readthedocs.io/en/latest/server/contents/conf.html
- **Session Management**: https://idpy-oidc.readthedocs.io/en/latest/server/contents/session_management.html
- **Client Database**: https://idpy-oidc.readthedocs.io/en/latest/server/contents/clients.html

### Standards

- **OAuth 2.0**: https://tools.ietf.org/html/rfc6749
- **OpenID Connect Core**: https://openid.net/specs/openid-connect-core-1_0.html
- **OIDC Discovery**: https://openid.net/specs/openid-connect-discovery-1_0.html
- **OAuth 2.0 Authorization Server Metadata**: https://tools.ietf.org/html/rfc8414

### Code References

- **Server Service**: `libs/infrastructure/services/oidc_server_service.py`
- **Auth Controller**: `apps/webapi/controllers/auth__controller.py`
- **Main Application**: `apps/webapi/main.py`

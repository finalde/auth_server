# Test Clients

This directory contains test clients for validating the auth_server OAuth2/OIDC implementation.

## Overview

The test clients demonstrate different OAuth2 flows and use cases. All Python clients use **[Authlib](https://docs.authlib.org/)** for OAuth2/OIDC client functionality, which provides automatic OIDC Discovery and spec-compliant token handling.

1. **Resource Server** - Protected API that validates OAuth2 tokens (uses Authlib)
2. **Batch Client** - Python script using Client Credentials flow (uses Authlib)
3. **SPA Client** - React SPA using Authorization Code flow with PKCE
4. **Caller WebAPI** - Service-to-service client using Authorization Code flow (uses Authlib)

## Quick Start

### 1. Start Auth Server

```bash
cd apps/webapi
python -m apps.webapi
# Runs on http://localhost:8000
```

### 2. Start Resource Server

```bash
cd test_clients/resource_server
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8001
```

### 3. Test with Batch Client

```bash
cd test_clients/batch_client
pip install -r requirements.txt
python main.py
```

### 4. Test with SPA Client

```bash
cd test_clients/spa_client
npm install
npm run dev
# Runs on http://localhost:3000
```

### 5. Test with Caller WebAPI

```bash
cd test_clients/caller_webapi
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8002
```

## OAuth2 Flows Demonstrated

### Client Credentials Flow (Batch Client)

**Use Case**: Machine-to-machine authentication, server-to-server communication

**Flow**:
1. Client uses Authlib to discover auth_server via OIDC Discovery
2. Client authenticates with `client_id` and `client_secret`
3. Auth server issues access token
4. Client uses token to access protected resources

**Client**: `batch_client/` (uses Authlib)

### Authorization Code Flow with PKCE (SPA Client)

**Use Case**: Single Page Applications, mobile apps

**Flow**:
1. Client generates PKCE code verifier/challenge
2. User redirected to authorization endpoint
3. User authorizes → receives authorization code
4. Client exchanges code + verifier for tokens
5. Client uses tokens to access resources

**Client**: `spa_client/` (React implementation)

### Authorization Code Flow (Caller WebAPI)

**Use Case**: Server-side web applications, services acting on behalf of users

**Flow**:
1. Service uses Authlib to discover auth_server
2. Service redirects user to authorization endpoint
3. User authorizes → redirected back with code
4. Service exchanges code for tokens (Authlib handles this)
5. ID token is validated automatically (Authlib)
6. Service uses tokens to call resources on user's behalf

**Client**: `caller_webapi/` (uses Authlib)

## Client Registration

Before using test clients, register them in the auth_server:

### Batch Client
- Client ID: `batch_client`
- Client Secret: `batch_secret`
- Grant Types: `client_credentials`
- Scopes: `api:read`

### SPA Client
- Client ID: `spa_client`
- Client Secret: `None` (public client)
- Grant Types: `authorization_code`, `refresh_token`
- Redirect URIs: `http://localhost:3000/callback`
- PKCE: Required

### Caller WebAPI
- Client ID: `caller_webapi`
- Client Secret: `caller_secret`
- Grant Types: `authorization_code`, `refresh_token`
- Redirect URIs: `http://localhost:8002/callback`
- Scopes: `openid profile api:read`

## Resource Server

The resource server (`resource_server/`) is a protected API that:
- Validates OAuth2 access tokens using **Authlib**
- Automatically configures itself via OIDC Discovery
- Demonstrates token validation patterns
- Shows how a Web API uses auth_server for authentication and authorization

**Endpoints**:
- `GET /` - Public endpoint
- `GET /protected` - Protected endpoint (requires Bearer token)
- `GET /api/data` - Protected data endpoint (requires Bearer token)

**Key Features**:
- ✅ Automatic OIDC Discovery
- ✅ JWT validation via JWKS
- ✅ Self-configuring (no hardcoded endpoints)
- ✅ Uses Authlib for spec-compliant implementation

## Login Page

The login page is part of the auth_server itself (not a separate test client). 
When clients redirect users to the authorization endpoint without authentication,
they are automatically redirected to `/api/v1/auth/login`.

The login page is located at `apps/webapi/templates/login.html` and is integrated
into the auth_server's authorization flow.

## Authlib Integration

All Python test clients use **[Authlib](https://docs.authlib.org/)** for OAuth2/OIDC client functionality:

### Why Authlib?

- ✅ **Spec-compliant**: Follows OAuth2/OIDC specifications strictly
- ✅ **OIDC Discovery**: Automatic server configuration via discovery endpoints
- ✅ **JWKS Support**: Automatic JWKS loading and key rotation
- ✅ **Framework Integration**: Clean integration with FastAPI, Flask, Django
- ✅ **Maintained**: Actively maintained and widely used
- ✅ **IdPyOIDC Compatible**: Works perfectly with IdPyOIDC servers

### Benefits

1. **Self-Configuring**: Clients automatically discover auth_server configuration
2. **No Manual Setup**: No need to hardcode endpoints or JWKS URIs
3. **Automatic Updates**: JWKS keys are refreshed automatically
4. **Production-Ready**: Battle-tested library used by many projects

## Testing Checklist

- [ ] Auth server running on port 8000
- [ ] Resource server running on port 8001
- [ ] Clients registered in auth server
- [ ] Batch client can get token and access resources
- [ ] SPA client can complete authorization flow
- [ ] Caller WebAPI can authenticate and call resources
- [ ] Tokens are properly validated by resource server
- [ ] OIDC Discovery works correctly
- [ ] JWKS validation works correctly

## Troubleshooting

### "Invalid client" errors
- Ensure clients are registered in auth_server
- Check client_id and client_secret match registration

### "Invalid redirect_uri" errors
- Ensure redirect_uri matches exactly what's registered
- Check for trailing slashes and protocol (http vs https)

### Token validation failures
- Check token hasn't expired
- Verify token is being sent in Authorization header
- Ensure resource server can reach auth server for JWKS
- Check OIDC Discovery is working (visit `/.well-known/openid-configuration`)

### CORS issues (SPA)
- Configure CORS in auth_server for SPA origin
- Check browser console for CORS errors

### Authlib Discovery Issues
- Verify auth_server discovery endpoint is accessible
- Check network connectivity between clients and auth_server
- Ensure discovery document is valid OIDC format

## Architecture

```
┌─────────────┐
│ Auth Server │ (Port 8000)
│  (IdPyOIDC) │
└──────┬──────┘
       │
       ├─── Issues tokens
       │    Provides OIDC Discovery
       │    Serves JWKS
       │
       ▼
┌─────────────┐
│   Clients   │
│             │
│ • Batch     │ (Client Credentials + Authlib)
│ • SPA       │ (Auth Code + PKCE)
│ • WebAPI    │ (Auth Code + Authlib)
└──────┬──────┘
       │
       │ Uses tokens
       │
       ▼
┌─────────────┐
│  Resource   │ (Port 8001)
│   Server    │
│             │
│ Authlib     │
│ validates   │
│ via JWKS    │
└─────────────┘
```

## Key Technologies

- **Authlib**: OAuth2/OIDC client library for Python
- **IdPyOIDC**: OAuth2/OIDC server (auth_server)
- **FastAPI**: Web framework for resource server and caller webapi
- **React**: Frontend framework for SPA client
- **OIDC Discovery**: Automatic server configuration

## Next Steps

- Add more test scenarios
- Implement token introspection
- Add user management UI
- Test refresh token flows
- Add error handling tests
- Performance testing
- Test with multiple issuers

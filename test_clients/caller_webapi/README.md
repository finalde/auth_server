# Caller WebAPI

A test webapi service that uses Authorization Code flow via **Authlib** to authenticate users and then calls the resource server on their behalf.

## OAuth2 Flow

This client uses the **Authorization Code Flow** (OAuth2 RFC 6749 Section 4.1), suitable for:
- Server-side web applications
- Services that need to act on behalf of users
- Services that can securely store client secrets

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the caller webapi:
```bash
python main.py
```

The server will run on `http://localhost:8002`

## Endpoints

- `GET /` - Root endpoint
- `GET /login` - Initiate OAuth2 login flow (redirects to auth server)
- `GET /callback` - OAuth2 callback endpoint
- `GET /call-resource` - Call protected resource on behalf of authenticated user

## Usage

1. Visit `http://localhost:8002/login` to start authentication
2. After authorization, you'll be redirected back to `/callback`
3. Visit `http://localhost:8002/call-resource` to access protected resources

## Features

- **OIDC Discovery**: Automatically discovers auth_server configuration
- **Authlib Integration**: Uses Authlib for spec-compliant OAuth2/OIDC client functionality
- **ID Token Validation**: Authlib automatically validates ID tokens
- **Token Management**: Handles token exchange and refresh

## Flow

1. User visits `/login` → redirects to auth server (via Authlib)
2. User authorizes → redirected to `/callback` with code
3. Service exchanges code for tokens (Authlib handles this)
4. ID token is validated automatically (Authlib)
5. Service uses access token to call resource server on user's behalf

## Authlib

This client uses [Authlib](https://docs.authlib.org/) for:
- OIDC Discovery integration
- Authorization redirect handling
- Token exchange
- ID token validation
- Clean FastAPI/Starlette integration

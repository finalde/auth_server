# Resource Server

A test resource server that protects its endpoints using OAuth2 access tokens from auth_server. It uses **Authlib** to automatically configure itself via OIDC Discovery and validate JWT tokens.

## Features

- **Automatic OIDC Discovery**: Automatically loads configuration from auth_server's discovery endpoint
- **JWT Validation**: Validates access tokens using JWKS from auth_server
- **Authlib Integration**: Uses Authlib for spec-compliant OAuth2/OIDC client functionality
- **Self-Configuring**: No hardcoded endpoints - discovers issuer, JWKS URI, etc.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The server will run on `http://localhost:8001`

## Endpoints

- `GET /` - Public endpoint (shows server info)
- `GET /protected` - Protected endpoint (requires Bearer token)
- `GET /api/data` - Protected data endpoint (requires Bearer token)

## Usage

Access protected endpoints with Authorization header:
```bash
curl -H "Authorization: Bearer <access_token>" http://localhost:8001/protected
```

## Configuration

The resource server automatically discovers configuration from the auth_server at `http://localhost:8000`.

It uses OIDC Discovery (`.well-known/openid-configuration`) to:
1. Discover the issuer
2. Get the JWKS URI
3. Load signing keys
4. Validate tokens against the correct issuer

Update `AUTH_SERVER_URL` in `main.py` if your auth server is at a different location.

## Architecture

```
┌─────────────┐
│ Auth Server │ (Port 8000)
│  (IdPyOIDC) │
└──────┬──────┘
       │
       │ Issues JWT tokens
       │
       ▼
┌─────────────┐      ┌──────────────┐
│   Client    │─────▶│ Resource     │
│             │      │ Server       │
│ Requests    │      │ (Authlib)    │
│ with token  │      │              │
└─────────────┘      │ Validates    │
                     │ via JWKS     │
                     └──────────────┘
```

## Authlib Integration

This server uses [Authlib](https://docs.authlib.org/) for:
- OIDC Discovery support
- JWT token validation
- JWKS key set handling
- Spec-compliant OAuth2/OIDC client functionality

The server automatically configures itself by:
1. Fetching the discovery document from auth_server
2. Loading JWKS from the discovered JWKS URI
3. Validating tokens using the issuer and keys

No manual configuration needed - it "self-sets up" from your auth_server!

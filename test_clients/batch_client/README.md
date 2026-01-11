# Batch Client

A Python batch script that uses the Client Credentials flow via **Authlib** to access protected resources.

## OAuth2 Flow

This client uses the **Client Credentials Flow** (OAuth2 RFC 6749 Section 4.4), which is suitable for:
- Server-to-server communication
- Machine-to-machine authentication
- Batch jobs and scheduled tasks

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure client credentials in `main.py`:
   - Update `CLIENT_ID` and `CLIENT_SECRET`
   - Ensure these credentials are registered in auth_server

3. Run the batch client:
```bash
python main.py
```

## Features

- **OIDC Discovery**: Automatically discovers auth_server configuration
- **Authlib Integration**: Uses Authlib for spec-compliant OAuth2 client functionality
- **Async Support**: Uses async/await for efficient I/O

## Flow

1. Client loads server metadata via OIDC Discovery
2. Client requests access token using client credentials
3. Auth server validates credentials and issues token
4. Client uses token to access protected resource server
5. Resource server validates token and returns data

## Authlib

This client uses [Authlib](https://docs.authlib.org/) for OAuth2 client functionality:
- Automatic OIDC Discovery
- Token exchange
- Spec-compliant implementation
- Clean async API

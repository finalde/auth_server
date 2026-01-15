# Test Application

A Python script that demonstrates calling both public and protected endpoints on the resource server using OAuth2 client credentials flow.

## Prerequisites

1. **Auth Server** must be running on `http://localhost:8000`
2. **Resource Server** must be running on `http://localhost:8001`
3. **Database** must be initialized with test data from `scripts/db/initial.sql`

## Test Data

The script uses the following test credentials (defined in `initial.sql`):
- **Client ID**: `test_client`
- **Client Secret**: `test_secret`
- **Scope**: `openid read write`

## Usage

```bash
# From project root
python test_clients/test_app/main.py

# Or using Python module
python -m test_clients.test_app.main
```

## What It Does

1. **Calls Public Endpoint** (`GET /`):
   - No authentication required
   - Demonstrates that public endpoints work without tokens

2. **Gets Access Token**:
   - Uses OAuth2 client credentials flow
   - Uses Authlib to discover token endpoint via OIDC Discovery
   - Exchanges client credentials for access token

3. **Calls Protected Endpoint** (`GET /protected`):
   - Requires valid access token
   - Resource server validates token using JWKS from auth server

4. **Calls Protected Data Endpoint** (`GET /api/data`):
   - Requires valid access token
   - Returns protected data

## Expected Output

```
============================================================
🧪 OAuth2/OIDC Test Application
============================================================
Auth Server: http://localhost:8000
Resource Server: http://localhost:8001
Client ID: test_client
Scope: openid read write

============================================================
📞 Calling PUBLIC endpoint (no auth required)
============================================================
✅ Status: 200
📄 Response:
{
  "message": "Resource Server API",
  "status": "public",
  ...
}

============================================================
🔑 Getting access token (client credentials flow)
============================================================
✅ Successfully obtained access token
   Token type: Bearer
   Expires in: 3600 seconds

============================================================
🔒 Calling PROTECTED endpoint (auth required)
============================================================
✅ Status: 200
📄 Response:
{
  "message": "This is a protected resource",
  "user": {...},
  ...
}
```

## Troubleshooting

### Error: "Failed to get access token"
- Check that auth server is running on port 8000
- Verify test client exists in database: `SELECT * FROM oauth2_clients WHERE client_id = 'test_client';`
- Check that client credentials are correct

### Error: "401 Unauthorized" on protected endpoint
- Verify access token was obtained successfully
- Check that resource server is running on port 8001
- Verify resource server can reach auth server's JWKS endpoint

### Error: "Connection refused"
- Ensure both auth server and resource server are running
- Check ports 8000 and 8001 are not in use by other applications

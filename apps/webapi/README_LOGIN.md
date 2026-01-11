# Login Page

The login page is integrated into the auth_server and is automatically used during the OAuth2 authorization flow.

## Starting the Auth Server

The login page is available once you start the auth_server:

### Option 1: Using Python module (Recommended)

```bash
# From project root
python -m apps.webapi
```

### Option 2: Using uvicorn directly

```bash
# From project root
uvicorn apps.webapi.main:app --reload
```

The server will start on `http://localhost:8000` (or the port configured in `config.yml`).

## Accessing the Login Page

### Direct Access

You can access the login page directly at:
```
http://localhost:8000/api/v1/auth/login
```

### With OAuth2 Parameters

The login page accepts OAuth2 authorization parameters as query string:

```
http://localhost:8000/api/v1/auth/login?client_id=my_client&redirect_uri=http://localhost:3000/callback&state=random_state&scope=openid profile
```

**Parameters:**
- `client_id` - OAuth2 client ID
- `redirect_uri` - Where to redirect after authorization
- `state` - CSRF protection state parameter
- `scope` - Requested OAuth2 scopes
- `response_type` - Usually "code"
- `code_challenge` - PKCE code challenge (if using PKCE)
- `code_challenge_method` - PKCE method (usually "S256")

### Automatic Redirect from Authorization Endpoint

When a client redirects users to the authorization endpoint without authentication:

```
GET http://localhost:8000/api/v1/auth/authorization?client_id=my_client&redirect_uri=...
```

The authorization endpoint will automatically redirect unauthenticated users to:
```
GET http://localhost:8000/api/v1/auth/login?client_id=my_client&redirect_uri=...
```

All OAuth2 parameters are preserved during the redirect.

## Testing the Login Flow

1. **Start the auth_server:**
   ```bash
   python -m apps.webapi
   ```

2. **Access login page directly:**
   ```
   http://localhost:8000/api/v1/auth/login
   ```

3. **Or test the full OAuth2 flow:**
   - Start a test client (e.g., SPA client)
   - The client will redirect to the authorization endpoint
   - If not authenticated, you'll be redirected to the login page
   - After login, you'll be redirected back to complete authorization

## Example: Testing with Test Clients

### With SPA Client

1. Start auth_server:
   ```bash
   python -m apps.webapi
   ```

2. Start SPA client:
   ```bash
   cd test_clients/spa_client
   npm install
   npm run dev
   ```

3. In browser, click "Login with OAuth2" in the SPA
4. You'll be redirected to the auth_server login page
5. Enter credentials and submit
6. After authentication, you'll complete the authorization flow

## Current Implementation Status

**✅ Implemented:**
- Login page UI
- Form submission handling
- OAuth2 parameter preservation
- Redirect flow integration

**⚠️ TODO (Placeholders in code):**
- Real user authentication (currently accepts any username/password)
- Session management (currently uses query parameters - not secure)
- Client name lookup (currently shows client_id)
- User consent screen (after login, before authorization)

## Security Notes

**Current implementation is for testing only!**

In production, you need to:
1. **Authenticate against user database** - Replace placeholder authentication
2. **Use secure sessions** - Don't pass user info via query parameters
3. **Hash passwords** - Never compare plaintext passwords
4. **Add rate limiting** - Prevent brute force attacks
5. **Add CSRF protection** - Protect against CSRF attacks
6. **Use HTTPS** - Always use HTTPS in production

## Configuration

The login page uses the same configuration as the auth_server. Update `apps/webapi/config.yml` to change:
- Server host/port
- Database connection (for user authentication)
- Session configuration

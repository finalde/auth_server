# Auth Server UI Guide

The auth server has different UI components depending on what you need.

## 1. OAuth2 Login Page (Part of WebAPI)

This is the **login page for OAuth2 authorization flows**. It's integrated into the auth_server webapi.

### Starting the Login Page

1. **Start the auth server:**
   ```bash
   python -m apps.webapi
   ```
   Or:
   ```bash
   uvicorn apps.webapi.main:app --reload
   ```

2. **Access the login page:**
   - Direct access: `http://localhost:8000/api/v1/auth/login`
   - With OAuth2 params: `http://localhost:8000/api/v1/auth/login?client_id=my_client&redirect_uri=...`

### When It's Used

- When a client redirects users to `/api/v1/auth/authorization` without authentication
- Users are automatically redirected to the login page
- After login, users complete the authorization flow

### Features

- ✅ OAuth2 login form
- ✅ Preserves OAuth2 parameters (client_id, redirect_uri, state, scope, etc.)
- ✅ Server-side form handling
- ⚠️ User authentication (placeholder - needs database integration)
- ⚠️ Session management (needs implementation)

## 2. Auth Server Management UI (Planned)

This would be a **React admin UI** for managing the auth server:
- Client management (CRUD)
- User management (CRUD)
- Scope/resource management
- OAuth2 flow testing
- Server monitoring

**Status**: Not yet implemented. The `apps/auth_ui` directory exists but is empty.

See `apps/auth_ui/README.md` for planned features.

## Quick Reference

### Start Auth Server (includes login page)
```bash
# From project root
python -m apps.webapi
```

### Access Login Page
```
http://localhost:8000/api/v1/auth/login
```

### Test Full Flow
1. Start auth server: `python -m apps.webapi`
2. Start a test client (e.g., SPA client)
3. Click "Login" in the client
4. You'll be redirected to the login page
5. Enter credentials and complete authorization

## Current Implementation Status

**Login Page** ✅
- UI is implemented
- Integrated into authorization flow
- Needs: Real user authentication, session management

**Management UI** ❌
- Not yet implemented
- Placeholder exists at `apps/auth_ui/`

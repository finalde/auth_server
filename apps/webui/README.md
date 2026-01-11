# WebUI Application

React Redux Web UI application for managing the Auth Server.

**Status**: Not yet implemented. This is a placeholder for the future management UI.

## Planned Features

The WebUI will provide:
- Client management (CRUD operations for OAuth2 clients)
- User management (CRUD operations for users)
- Scope management
- Resource management
- OAuth2 flow testing tools
- Server configuration
- Monitoring and logs

## Current Auth Server UI

Currently, the auth server has:
- **Login Page**: Available at `/api/v1/auth/login` (integrated into webapi)
  - This is the OAuth2 login page used during authorization flows
  - Access it by starting the auth server:
    ```bash
    python -m apps.webapi
    ```
  - Then visit: `http://localhost:8000/api/v1/auth/login`

## Setup (When Implemented)

1. Install dependencies:
```bash
cd apps/webui
npm install
```

2. Configure API endpoint (point to auth_server):
```bash
# Set in .env or config
REACT_APP_API_URL=http://localhost:8000
```

3. Run the application:
```bash
npm start
```

The UI will be available at `http://localhost:3000` (or configured port).

## Architecture

- `src/components/` - React components
- `src/store/` - Redux store configuration
- `src/actions/` - Redux actions
- `src/reducers/` - Redux reducers
- `src/services/` - API client services (communicate with auth_server webapi)

# AuthUI Rename Summary

## What Was Done

The `webui` directory has been renamed to `auth_ui` to better reflect its purpose as an admin management UI.

## Changes Made

### 1. Directory Renamed ✅
- `apps/webui/` → `apps/auth_ui/`

### 2. Documentation Updated ✅
- **ARCHITECTURE.md**: Updated all references from WebUI to AuthUI
- **README.md**: Updated project structure and setup instructions
- **README_UI.md**: Updated references to auth_ui directory
- **apps/auth_ui/README.md**: Updated with new name and purpose

### 3. Configuration Files Updated ✅
- **.gitignore**: Updated paths from `apps/webui/` to `apps/auth_ui/`
- **package.json**: Updated name from `auth-server-webui` to `auth-server-auth-ui`

## Purpose of AuthUI

The AuthUI is a React SPA admin interface for managing the auth server. It provides:

### Core Features
- **Client Management**: CRUD operations for OAuth2 clients
- **User Management**: CRUD operations for users
- **Resource Management**: CRUD operations for resources
- **Scope Management**: CRUD operations for scopes
- **Access Control**: Grant/revoke user access to resources and scopes

### Admin Operations
- Add new resources to the database
- Grant users access to resource endpoints
- Manage user-scope assignments
- Configure OAuth2 clients
- View and manage permissions

## Architecture

The AuthUI follows the same architectural principles as the WebAPI:
- **Application Boundary**: Can only depend on `application/` layer (DTOs, queries, commands)
- **No Direct Access**: Cannot access `domain/` or `infrastructure/` directly
- **DTO Flow**: All data flows through DTOs
- **Dependency Injection**: Uses DI container for services

## Next Steps

When implementing the AuthUI:
1. Set up React project structure in `apps/auth_ui/`
2. Implement authentication using OAuth2/OIDC (authenticate against the auth server)
3. Create API client services that call WebAPI endpoints
4. Implement CRUD components for clients, users, resources, scopes
5. Implement access control UI for managing user permissions
6. Add admin-specific scopes (e.g., `admin`, `manage.clients`, `manage.users`)

# AuthUI Application

React SPA Admin UI application for managing the Auth Server.

## Quick Start

1. Install dependencies:
```bash
cd apps/auth_ui
npm install
```

2. Run the application:
```bash
npm run dev
```

The UI will be available at `http://localhost:3001`.

## Features

### Layout
- **Top Bar**: Shows app title and user info with logout button
- **Left Sidebar**: Navigation menu with links to Dashboard, Clients, Users, Resources, Scopes
- **Main Panel**: Content area for each page

### Management Pages

#### Dashboard
- Overview of the auth server
- Quick stats cards

#### Clients
- View all OAuth2 clients
- Create new clients
- Edit existing clients
- Delete clients
- Fields: client_name, redirect_uris, grant_types, scopes, etc.

#### Users
- View all users
- Create new users
- Edit existing users
- Delete users
- Fields: username, email, password, first_name, last_name, status

#### Resources
- View all resources
- Create new resources
- Edit existing resources
- Delete resources
- Fields: resource_name, resource_uri, scopes, description

#### Scopes
- View all scopes
- Create new scopes
- Edit existing scopes
- Delete scopes
- Fields: scope_name, description

## API Integration

The AuthUI communicates with the WebAPI at `http://localhost:8000/api/v1`:
- `/clients` - Client management
- `/users` - User management
- `/resources` - Resource management
- `/scopes` - Scope management

All API calls include the access token from localStorage in the Authorization header.

## Authentication

Currently, authentication is not implemented. The UI assumes you have a valid access token in localStorage.

**TODO**: Implement OAuth2/OIDC authentication flow for admin users.

## Project Structure

```
apps/auth_ui/
├── src/
│   ├── components/     # Reusable components (Layout, TopBar, Sidebar)
│   ├── pages/         # Page components (ClientsPage, UsersPage, etc.)
│   ├── services/      # API service layer
│   ├── types.ts       # TypeScript type definitions
│   ├── App.tsx        # Main app component with routing
│   └── main.tsx       # Entry point
├── package.json
├── vite.config.ts
└── tsconfig.json
```

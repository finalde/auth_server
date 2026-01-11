# SPA Client

A React Single Page Application (SPA) that uses OAuth2 Authorization Code flow with PKCE to authenticate and access protected resources.

## OAuth2 Flow

This client uses the **Authorization Code Flow with PKCE** (RFC 7636), which is the recommended flow for:
- Single Page Applications (SPAs)
- Mobile applications
- Public clients (clients that cannot securely store secrets)

## Setup

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

The app will run on `http://localhost:3000`

## Features

- OAuth2 Authorization Code flow with PKCE
- Automatic token refresh
- Protected resource access
- User info display
- Clean, modern UI

## Usage

1. Click "Login with OAuth2" button
2. You'll be redirected to the auth server
3. After authorization, you'll be redirected back
4. The app will automatically exchange the code for tokens
5. Protected resources will be displayed

## Configuration

Update these constants in `src/App.tsx` if needed:
- `AUTH_SERVER_URL` - Auth server base URL
- `RESOURCE_SERVER_URL` - Resource server base URL
- `CLIENT_ID` - Your OAuth2 client ID
- `REDIRECT_URI` - Callback URL (must match registration)

## Client Registration

Register this client in auth_server with:
- Client ID: `spa_client`
- Client Secret: `None` (public client)
- Grant Types: `authorization_code`, `refresh_token`
- Redirect URIs: `http://localhost:3000/callback`
- PKCE: Required (code_challenge_method: S256)

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

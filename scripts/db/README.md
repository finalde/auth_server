# Database Scripts

This directory contains database schema and migration scripts.

## Scripts

### initial.sql

Creates the initial database schema with all tables:
- `scopes` - OAuth2 scopes
- `users` - User accounts
- `oauth2_clients` - OAuth2 client applications
- `resources` - Protected resources/APIs

**Note**: This script is rerunnable - it drops tables if they exist before creating them.

## Usage

### PostgreSQL

```bash
# Connect to PostgreSQL and run the script
psql -U username -d database_name -f scripts/db/initial.sql

# Or using environment variables
psql $DATABASE_URL -f scripts/db/initial.sql
```

### Using psql directly

```bash
psql -U postgres -d auth_server -f scripts/db/initial.sql
```

## Features

- **Rerunnable**: Uses `DROP TABLE IF EXISTS` before creating tables
- **Indexes**: Includes indexes for commonly queried fields
- **Triggers**: Automatically updates `updated_at` timestamp on row updates
- **Constraints**: Includes primary keys, unique constraints, and NOT NULL constraints
- **Array Support**: Uses PostgreSQL TEXT[] arrays for multi-value fields

## Table Structure

### scopes
- `scope_name` (PRIMARY KEY)
- `description`
- `is_active`
- `created_at`, `updated_at`

### users
- `id` (PRIMARY KEY)
- `user_id` (UNIQUE)
- `username` (UNIQUE)
- `email` (UNIQUE)
- `password_hash`
- `status`
- `first_name`, `last_name`
- `is_active`
- `created_at`, `updated_at`

### oauth2_clients
- `id` (PRIMARY KEY)
- `client_id` (UNIQUE)
- `client_secret`
- `client_name`, `client_uri`
- `redirect_uris` (TEXT[])
- `grant_types` (TEXT[])
- `response_types` (TEXT[])
- `scopes` (TEXT[])
- `logo_uri`, `tos_uri`, `policy_uri`
- `is_active`
- `created_at`, `updated_at`

### resources
- `id` (PRIMARY KEY)
- `resource_id` (UNIQUE)
- `resource_name`, `resource_uri`
- `scopes` (TEXT[])
- `description`
- `is_active`
- `created_at`, `updated_at`

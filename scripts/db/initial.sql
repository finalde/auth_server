-- Initial database schema creation
-- This script is rerunnable: it drops tables if they exist before creating them

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS oauth2_clients CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS user_scopes CASCADE;
DROP TABLE IF EXISTS user_claims CASCADE;
DROP TABLE IF EXISTS resources CASCADE;
DROP TABLE IF EXISTS scopes CASCADE;

-- Create scopes table
CREATE TABLE scopes (
    scope_name VARCHAR(100) PRIMARY KEY,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed default scopes for Auth UI and OIDC
INSERT INTO scopes (scope_name, description, is_active)
VALUES
    ('openid', 'OpenID Connect base scope', TRUE),
    ('admin', 'Administrative access', TRUE),
    ('manage.clients', 'Manage OAuth2 clients', TRUE),
    ('manage.users', 'Manage users', TRUE),
    ('manage.resources', 'Manage protected resources', TRUE),
    ('manage.scopes', 'Manage scopes', TRUE)
ON CONFLICT (scope_name) DO NOTHING;

-- Create users table
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create user_claims table for structured user-level claims
-- OAuth2/OIDC Best Practice:
-- - Scopes = what the client/app is allowed to do (permissions)
-- - Claims = who the user IS (roles, tenant, flags), used as constraints in policies
-- This table stores user attributes that can be turned into token claims (via userinfo).
CREATE TABLE IF NOT EXISTS user_claims (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    claim_name VARCHAR(255) NOT NULL,
    claim_value TEXT NOT NULL,
    claim_type VARCHAR(50),  -- Optional: 'string', 'number', 'boolean', 'json'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, claim_name)
);

-- Create indexes for user_claims table
CREATE INDEX IF NOT EXISTS idx_user_claims_user_id ON user_claims(user_id);
CREATE INDEX IF NOT EXISTS idx_user_claims_claim_name ON user_claims(claim_name);

-- Create user_scopes table for per-user scope grants
-- This models user-level permissions:
-- - Scopes still remain the permission signal in the token
-- - user_scopes constrains WHICH scopes a given user is allowed to receive
CREATE TABLE IF NOT EXISTS user_scopes (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL,
    scope_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (scope_name) REFERENCES scopes(scope_name) ON DELETE RESTRICT,
    UNIQUE(user_id, scope_name)
);

-- Create indexes for user_scopes table
CREATE INDEX IF NOT EXISTS idx_user_scopes_user_id ON user_scopes(user_id);
CREATE INDEX IF NOT EXISTS idx_user_scopes_scope_name ON user_scopes(scope_name);

-- Create indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create oauth2_clients table
CREATE TABLE oauth2_clients (
    id VARCHAR(36) PRIMARY KEY,
    client_id VARCHAR(255) UNIQUE NOT NULL,
    client_secret VARCHAR(255) NOT NULL,
    client_name VARCHAR(255),
    client_uri VARCHAR(512),
    redirect_uris TEXT[],  -- Array of strings in PostgreSQL
    grant_types TEXT[],
    response_types TEXT[],
    scopes TEXT[],  -- OAuth2 scopes (what the client CAN DO): data.read, data.write, etc.
                    -- NOTE: For production, consider a client_scopes join table instead of TEXT[]
                    -- This provides referential integrity, easier queries, and cleaner revocation
    metadata JSONB,  -- Custom claims (attributes/constraints): WHO/WHAT the client IS
                     -- Examples: organization_id, trust_level, tenant_id, env
                     -- Use client_claims table for structured claims, metadata for simple cases
    logo_uri VARCHAR(512),
    tos_uri VARCHAR(512),
    policy_uri VARCHAR(512),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for oauth2_clients table
CREATE INDEX IF NOT EXISTS idx_oauth2_clients_client_id ON oauth2_clients(client_id);
CREATE INDEX IF NOT EXISTS idx_oauth2_clients_metadata ON oauth2_clients USING GIN (metadata);

-- Create client_claims table for structured client-level claims
-- OAuth2 Best Practice: Claims are attributes (constraints), NOT permissions
-- Claims should be independent of scopes - they describe WHO/WHAT the client IS, not what it can DO
-- This is useful when you need many structured claims (organization_id, client_role, tier, etc.)
-- For simple cases, use the metadata JSONB column in oauth2_clients instead
--
-- IMPORTANT: Do NOT create a scope_claim table - this is an anti-pattern
-- Scopes should never generate claims. Claims come from client identity, not scope membership.
-- Scope = permission to act, Claim = constraint on how/where/for whom
CREATE TABLE IF NOT EXISTS client_claims (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    client_id VARCHAR(255) NOT NULL,
    claim_name VARCHAR(255) NOT NULL,
    claim_value TEXT NOT NULL,
    claim_type VARCHAR(50),  -- Optional: 'string', 'number', 'boolean', 'json'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES oauth2_clients(client_id) ON DELETE CASCADE,
    UNIQUE(client_id, claim_name)
);

-- Create indexes for client_claims table
CREATE INDEX IF NOT EXISTS idx_client_claims_client_id ON client_claims(client_id);
CREATE INDEX IF NOT EXISTS idx_client_claims_claim_name ON client_claims(claim_name);

-- Create resources table
CREATE TABLE resources (
    id VARCHAR(36) PRIMARY KEY,
    resource_id VARCHAR(36) UNIQUE NOT NULL,
    resource_name VARCHAR(255) NOT NULL,
    resource_uri VARCHAR(512) NOT NULL,
    scopes TEXT[],
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for resources table
CREATE INDEX IF NOT EXISTS idx_resources_resource_id ON resources(resource_id);
CREATE INDEX IF NOT EXISTS idx_resources_resource_uri ON resources(resource_uri);

-- Create updated_at trigger function (if not exists)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update updated_at column
DROP TRIGGER IF EXISTS update_scopes_updated_at ON scopes;
CREATE TRIGGER update_scopes_updated_at
    BEFORE UPDATE ON scopes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_oauth2_clients_updated_at ON oauth2_clients;
CREATE TRIGGER update_oauth2_clients_updated_at
    BEFORE UPDATE ON oauth2_clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_resources_updated_at ON resources;
CREATE TRIGGER update_resources_updated_at
    BEFORE UPDATE ON resources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TEST DATA FOR OAUTH2/OIDC TESTING
-- ============================================================================
-- This section contains test data for testing the OAuth2/OIDC flow:
-- - Test client for client credentials flow
-- - Test user for authorization code flow
-- - Test resource API
-- - Test scopes

-- Insert test scopes
-- Best Practice: Use resource-oriented scopes (data.read, data.write) instead of generic verbs
-- This follows OAuth2 best practices for microservices and avoids scope explosion
INSERT INTO scopes (scope_name, description, is_active) VALUES
    ('openid', 'OpenID Connect scope', TRUE),
    ('data.read', 'Read access to data API (resource-oriented scope)', TRUE),
    ('data.write', 'Write access to data API (resource-oriented scope)', TRUE),
    ('read', 'Legacy read scope (deprecated, use data.read)', TRUE),  -- Keep for backward compatibility
    ('write', 'Legacy write scope (deprecated, use data.write)', TRUE),  -- Keep for backward compatibility
    ('admin', 'Administrative access to resources', TRUE),
    ('manage.clients', 'Manage OAuth2 clients (admin scope)', TRUE),
    ('manage.users', 'Manage users (admin scope)', TRUE),
    ('manage.resources', 'Manage resources (admin scope)', TRUE),
    ('manage.scopes', 'Manage scopes (admin scope)', TRUE)
ON CONFLICT (scope_name) DO NOTHING;

-- Insert test user (password: password123)
-- Password hash generated with bcrypt: $2b$12$bhq3uu2qOAeWWihj3bDrNOKy9fC6xnFbB0xP7Ct/Y5y4bAQy2npHC
INSERT INTO users (id, user_id, username, email, password_hash, status, first_name, last_name, is_active) VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'user-001', 'testuser', 'testuser@example.com', '$2b$12$bhq3uu2qOAeWWihj3bDrNOKy9fC6xnFbB0xP7Ct/Y5y4bAQy2npHC', 'active', 'Test', 'User', TRUE),
    ('660e8400-e29b-41d4-a716-446655440001', 'user-002', 'admin', 'admin@example.com', '$2b$12$bhq3uu2qOAeWWihj3bDrNOKy9fC6xnFbB0xP7Ct/Y5y4bAQy2npHC', 'active', 'Admin', 'User', TRUE)
ON CONFLICT (id) DO NOTHING;

-- Insert sample user claims for testuser
-- Example: role = 'reader' (can be used by resource server policies)
INSERT INTO user_claims (user_id, claim_name, claim_value, claim_type, is_active) VALUES
    ('user-001', 'role', 'reader', 'string', TRUE)
ON CONFLICT (user_id, claim_name) DO NOTHING;

-- Insert sample per-user scopes for testuser
-- testuser is allowed data.read but NOT data.write
INSERT INTO user_scopes (user_id, scope_name, is_active) VALUES
    ('user-001', 'data.read', TRUE)
ON CONFLICT (user_id, scope_name) DO NOTHING;

-- Insert admin user scopes
-- admin user has all management scopes
INSERT INTO user_scopes (user_id, scope_name, is_active) VALUES
    ('user-002', 'openid', TRUE),
    ('user-002', 'manage.clients', TRUE),
    ('user-002', 'manage.users', TRUE),
    ('user-002', 'manage.resources', TRUE),
    ('user-002', 'manage.scopes', TRUE),
    ('user-002', 'admin', TRUE)
ON CONFLICT (user_id, scope_name) DO NOTHING;

-- Insert test OAuth2 client for client credentials flow
-- Client ID: test_client
-- Client Secret: test_secret
-- This client has data.read scope but not data.write (demonstrates read-only access)
-- Metadata contains claims: trust_level='partner' (not 'internal', so cannot write)
INSERT INTO oauth2_clients (
    id,
    client_id,
    client_secret,
    client_name,
    redirect_uris,
    grant_types,
    response_types,
    scopes,
    metadata,
    is_active
) VALUES (
    '660e8400-e29b-41d4-a716-446655440000',
    'test_client',
    'test_secret',
    'Test Client Application (Read-Only)',
    ARRAY['http://localhost:9000/callback'],
    ARRAY['authorization_code', 'client_credentials', 'refresh_token'],
    ARRAY['code'],
    ARRAY['openid', 'data.read'],  -- Resource-oriented scope: can read data
    '{"trust_level": "partner", "tenant_id": "t-123", "env": "prod"}'::jsonb,  -- Claims: constraints on permissions
    TRUE
)
ON CONFLICT (id) DO NOTHING;

-- Insert SPA client for authorization code flow
-- Client ID: spa_client
-- No client secret (public client)
-- This client uses authorization_code flow with PKCE for SPA
INSERT INTO oauth2_clients (
    id,
    client_id,
    client_secret,
    client_name,
    redirect_uris,
    grant_types,
    response_types,
    scopes,
    is_active
) VALUES (
    '880e8400-e29b-41d4-a716-446655440000',
    'spa_client',
    '',  -- Public client, no secret required
    'SPA Client Application',
    ARRAY['http://localhost:3000/callback'],
    ARRAY['authorization_code', 'refresh_token'],
    ARRAY['code'],
    ARRAY['openid', 'data.read', 'data.write', 'read', 'write', 'admin'],  -- Include both resource-oriented and legacy scopes
    TRUE
),
(
    '990e8400-e29b-41d4-a716-446655440000',
    'auth_ui',
    '',  -- Public client, no secret required
    'Auth Server Admin UI',
    ARRAY['http://localhost:3001/callback'],
    ARRAY['authorization_code', 'refresh_token'],
    ARRAY['code'],
    ARRAY['openid', 'manage.clients', 'manage.users', 'manage.resources', 'manage.scopes', 'admin'],
    TRUE
)
ON CONFLICT (id) DO NOTHING;

-- Insert test resource API
-- This represents the resource server that needs to be protected
INSERT INTO resources (
    id,
    resource_id,
    resource_name,
    resource_uri,
    scopes,
    description,
    is_active
) VALUES (
    '770e8400-e29b-41d4-a716-446655440000',
    'resource-001',
    'Test Resource API',
    'http://localhost:8001',
    ARRAY['read', 'write'],
    'Test resource server for OAuth2/OIDC testing',
    TRUE
),
(
    '880e8400-e29b-41d4-a716-446655440001',
    'resource-002',
    'Auth Server WebAPI',
    'http://localhost:8000',
    ARRAY['manage.clients', 'manage.users', 'manage.resources', 'manage.scopes', 'admin'],
    'Auth server WebAPI for managing clients, users, resources, and scopes',
    TRUE
)
ON CONFLICT (id) DO NOTHING;

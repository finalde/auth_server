-- Initial database schema creation
-- This script is rerunnable: it drops tables if they exist before creating them

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS oauth2_clients CASCADE;
DROP TABLE IF EXISTS users CASCADE;
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

-- Create indexes for users table
CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

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
    scopes TEXT[],
    logo_uri VARCHAR(512),
    tos_uri VARCHAR(512),
    policy_uri VARCHAR(512),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for oauth2_clients table
CREATE INDEX idx_oauth2_clients_client_id ON oauth2_clients(client_id);

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
CREATE INDEX idx_resources_resource_id ON resources(resource_id);
CREATE INDEX idx_resources_resource_uri ON resources(resource_uri);

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
INSERT INTO scopes (scope_name, description, is_active) VALUES
    ('openid', 'OpenID Connect scope', TRUE),
    ('read', 'Read access to resources', TRUE),
    ('write', 'Write access to resources', TRUE)
ON CONFLICT (scope_name) DO NOTHING;

-- Insert test user (password: password123)
-- Password hash generated with bcrypt: $2b$12$bhq3uu2qOAeWWihj3bDrNOKy9fC6xnFbB0xP7Ct/Y5y4bAQy2npHC
INSERT INTO users (id, user_id, username, email, password_hash, status, first_name, last_name, is_active) VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'user-001', 'testuser', 'testuser@example.com', '$2b$12$bhq3uu2qOAeWWihj3bDrNOKy9fC6xnFbB0xP7Ct/Y5y4bAQy2npHC', 'active', 'Test', 'User', TRUE)
ON CONFLICT (id) DO NOTHING;

-- Insert test OAuth2 client for client credentials flow
-- Client ID: test_client
-- Client Secret: test_secret
-- This client can use client_credentials grant type to get access tokens
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
    '660e8400-e29b-41d4-a716-446655440000',
    'test_client',
    'test_secret',
    'Test Client Application',
    ARRAY['http://localhost:9000/callback'],
    ARRAY['authorization_code', 'client_credentials', 'refresh_token'],
    ARRAY['code'],
    ARRAY['openid', 'read', 'write'],
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
)
ON CONFLICT (id) DO NOTHING;

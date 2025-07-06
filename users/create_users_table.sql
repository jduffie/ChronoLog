-- Create users table for user profiles and preferences
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(30) UNIQUE NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    unit_system VARCHAR(20) NOT NULL DEFAULT 'Imperial', -- 'Imperial' or 'Metric'
    profile_complete BOOLEAN DEFAULT FALSE,
    auth0_sub VARCHAR(255),
    picture VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_auth0_sub ON users(auth0_sub);

-- Create trigger to auto-update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Add constraints
ALTER TABLE users ADD CONSTRAINT chk_unit_system CHECK (unit_system IN ('Imperial', 'Metric'));
ALTER TABLE users ADD CONSTRAINT chk_username_length CHECK (LENGTH(username) >= 3 AND LENGTH(username) <= 30);
ALTER TABLE users ADD CONSTRAINT chk_username_format CHECK (username ~ '^[a-zA-Z0-9_-]+$');

-- Add comments for documentation
COMMENT ON TABLE users IS 'User profiles and preferences';
COMMENT ON COLUMN users.email IS 'User email address from Auth0';
COMMENT ON COLUMN users.name IS 'Full name from Auth0';
COMMENT ON COLUMN users.username IS 'Unique username chosen by user';
COMMENT ON COLUMN users.state IS 'State or province where user is located';
COMMENT ON COLUMN users.country IS 'Country where user is located';
COMMENT ON COLUMN users.unit_system IS 'Preferred unit system: Imperial or Metric';
COMMENT ON COLUMN users.profile_complete IS 'Whether user has completed profile setup';
COMMENT ON COLUMN users.auth0_sub IS 'Auth0 subject identifier';
COMMENT ON COLUMN users.picture IS 'URL to user profile picture from Auth0';
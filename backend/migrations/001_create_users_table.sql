-- Migration: 001_create_users_table
-- Description: Create users table with UUID primary key and email uniqueness
-- Breaking: NO
-- Date: 2026-02-06

BEGIN;

-- Enable UUID extension for uuid_generate_v4() function
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: users
-- Purpose: Store authenticated user accounts
-- Relationships: One User has many Tasks (1:N)
CREATE TABLE users (
    -- Primary key: UUID for security (prevents enumeration attacks)
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Email: Unique identifier for authentication
    -- Constraint: UNIQUE ensures no duplicate accounts
    email VARCHAR(255) UNIQUE NOT NULL,

    -- Password: Always stored as bcrypt hash (cost factor 12)
    -- Security: Never store plain text passwords
    hashed_password VARCHAR(255) NOT NULL,

    -- Audit field: Account creation timestamp
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index: idx_user_email
-- Purpose: Fast email lookup for authentication (login queries)
-- Rationale: Email is used in WHERE clause for signin endpoint
CREATE UNIQUE INDEX idx_user_email ON users(email);

-- Verify migration
SELECT 'Users table created successfully' AS status;

COMMIT;

-- DOWN Migration (for rollback)
-- Uncomment to rollback this migration:
-- BEGIN;
-- DROP TABLE IF EXISTS users CASCADE;
-- COMMIT;

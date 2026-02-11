-- Migration: 002_create_tasks_table
-- Description: Create tasks table with foreign key to users and indexes for performance
-- Breaking: NO
-- Date: 2026-02-06
-- Prerequisites: 001_create_users_table.sql must be run first

BEGIN;

-- Table: tasks
-- Purpose: Store todo items owned by users
-- Relationships: Many Tasks belong to one User (N:1)
CREATE TABLE tasks (
    -- Primary key: UUID for security (prevents enumeration attacks)
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign key: Links task to owning user
    -- Constraint: REFERENCES users(id) ensures referential integrity
    -- ON DELETE CASCADE: When user is deleted, all their tasks are automatically deleted
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Task content: Title is required
    title VARCHAR(200) NOT NULL,

    -- Task content: Description is optional
    description TEXT,

    -- Task status: Defaults to incomplete
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,

    -- Audit fields: Track creation and modification times
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index: idx_task_user_id
-- Purpose: Fast filtering by user_id (critical for data isolation)
-- Rationale: ALL task queries filter by user_id to enforce security
-- Query pattern: SELECT * FROM tasks WHERE user_id = ?
CREATE INDEX idx_task_user_id ON tasks(user_id);

-- Index: idx_task_user_created
-- Purpose: Optimized for user's task list sorted by creation date
-- Rationale: Dashboard displays tasks sorted by created_at DESC
-- Query pattern: SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC
CREATE INDEX idx_task_user_created ON tasks(user_id, created_at DESC);

-- Verify migration
SELECT 'Tasks table created successfully' AS status;
SELECT 'Foreign key constraint on user_id created' AS status;
SELECT 'Indexes created: idx_task_user_id, idx_task_user_created' AS status;

COMMIT;

-- DOWN Migration (for rollback)
-- Uncomment to rollback this migration:
-- BEGIN;
-- DROP TABLE IF EXISTS tasks CASCADE;
-- COMMIT;

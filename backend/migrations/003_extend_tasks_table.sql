-- Migration 003: Extend tasks table with advanced features
-- Feature: 005-advanced-features-dapr-kafka

-- Install pg_trgm for full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Add new columns to tasks table
ALTER TABLE tasks
  ADD COLUMN IF NOT EXISTS priority VARCHAR(10) NOT NULL DEFAULT 'medium',
  ADD COLUMN IF NOT EXISTS due_date TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS recurrence_rule TEXT,
  ADD COLUMN IF NOT EXISTS series_id UUID,
  ADD COLUMN IF NOT EXISTS parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS is_paused BOOLEAN NOT NULL DEFAULT false;

-- Priority constraint
ALTER TABLE tasks
  ADD CONSTRAINT chk_priority CHECK (priority IN ('high', 'medium', 'low'));

-- GIN index for full-text search (pg_trgm)
CREATE INDEX IF NOT EXISTS idx_task_search_gin
  ON tasks USING GIN ((title || ' ' || COALESCE(description, '')) gin_trgm_ops);

-- Index for priority filtering
CREATE INDEX IF NOT EXISTS idx_task_priority ON tasks(user_id, priority);

-- Index for due date filtering (sparse — only rows with due_date)
CREATE INDEX IF NOT EXISTS idx_task_due_date
  ON tasks(user_id, due_date) WHERE due_date IS NOT NULL;

-- Composite cursor index for stable pagination
CREATE INDEX IF NOT EXISTS idx_task_cursor
  ON tasks(user_id, created_at DESC, id DESC);

-- Migration 005: Create tags table (user-scoped)
-- Feature: 005-advanced-features-dapr-kafka

CREATE TABLE IF NOT EXISTS tags (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(50) NOT NULL CHECK (name ~ '^[a-zA-Z0-9\-]+$'),
  color VARCHAR(7),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, name)
);

CREATE INDEX IF NOT EXISTS idx_tag_user_name ON tags(user_id, name);

-- Migration 007: Create recurrence_series table
-- Feature: 005-advanced-features-dapr-kafka

CREATE TABLE IF NOT EXISTS recurrence_series (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  original_task_id UUID NOT NULL REFERENCES tasks(id),
  recurrence_rule TEXT NOT NULL,
  base_title VARCHAR(200) NOT NULL,
  base_description TEXT,
  base_priority VARCHAR(10) NOT NULL DEFAULT 'medium'
    CHECK (base_priority IN ('high', 'medium', 'low')),
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_series_user ON recurrence_series(user_id);

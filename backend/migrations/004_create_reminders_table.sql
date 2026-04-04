-- Migration 004: Create reminders table
-- Feature: 005-advanced-features-dapr-kafka

CREATE TABLE IF NOT EXISTS reminders (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  offset_minutes INTEGER NOT NULL CHECK (offset_minutes > 0),
  trigger_at TIMESTAMPTZ NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'sent', 'cancelled')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Sparse index for polling pending reminders by trigger time
CREATE INDEX IF NOT EXISTS idx_reminder_trigger
  ON reminders(trigger_at) WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_reminder_task ON reminders(task_id);
CREATE INDEX IF NOT EXISTS idx_reminder_user ON reminders(user_id);

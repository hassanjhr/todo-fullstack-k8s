/**
 * Reminder Type Definitions
 * Feature: 005-advanced-features-dapr-kafka
 */

export interface Reminder {
  id: string;
  offset_minutes: number;
  trigger_at: string;
  status: 'pending' | 'sent' | 'cancelled';
}

export interface ReminderCreatePayload {
  offset_minutes: number;
}

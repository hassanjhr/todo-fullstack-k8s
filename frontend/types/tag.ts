/**
 * Tag Type Definitions
 * Feature: 005-advanced-features-dapr-kafka
 */

export interface Tag {
  id: string;
  name: string;
  color?: string | null;
  task_count: number;
}

export interface TagCreatePayload {
  name: string;
  color?: string;
}

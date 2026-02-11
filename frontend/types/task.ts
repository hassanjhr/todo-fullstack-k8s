/**
 * Task Type Definitions
 * Feature: 003-frontend-integration
 */

export interface Task {
  id: number;
  title: string;
  completed: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskData {
  title: string;
}

export interface UpdateTaskData {
  title?: string;
  completed?: boolean;
}

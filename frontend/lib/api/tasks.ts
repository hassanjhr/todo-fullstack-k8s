/**
 * Task API Client
 * Feature: 003-frontend-integration
 *
 * API functions for task CRUD operations
 */

import { apiClient } from './client';
import { Task, CreateTaskData, UpdateTaskData } from '@/types';
import { getUser } from '@/lib/auth/token';

/**
 * Get user ID from stored user data
 */
function getUserId(): string {
  const user = getUser();
  if (!user || !user.id) {
    throw new Error('User not authenticated');
  }
  return user.id;
}

/**
 * Get all tasks for the authenticated user
 */
export async function getTasks(): Promise<Task[]> {
  const userId = getUserId();
  const response = await apiClient.get<{ tasks: Task[] }>(`/api/${userId}/tasks`, true);
  return response.tasks;
}

/**
 * Create a new task
 */
export async function createTask(data: CreateTaskData): Promise<Task> {
  const userId = getUserId();
  return apiClient.post<Task>(`/api/${userId}/tasks`, data, true);
}

/**
 * Update an existing task (title and/or description)
 *
 * IMPORTANT: Backend validation requires:
 * - PUT /api/{user_id}/tasks/{task_id} expects {title: string, description?: string}
 * - is_completed is NOT updatable via PUT (use PATCH /complete instead)
 */
export async function updateTask(id: string, data: UpdateTaskData): Promise<Task> {
  const userId = getUserId();

  // If only updating completion status, use the PATCH /complete endpoint
  if ('is_completed' in data && Object.keys(data).length === 1) {
    console.log('[Tasks API] Toggling completion via PATCH /complete');
    return toggleTaskCompletion(id);
  }

  // For title/description updates, use PUT with required title field
  console.log('[Tasks API] Updating task via PUT with data:', data);
  return apiClient.put<Task>(`/api/${userId}/tasks/${id}`, data, true);
}

/**
 * Toggle task completion status
 *
 * Uses PATCH /api/{user_id}/tasks/{task_id}/complete endpoint
 * No request body needed - backend toggles the is_completed field automatically
 */
export async function toggleTaskCompletion(id: string): Promise<Task> {
  const userId = getUserId();
  console.log('[Tasks API] Calling PATCH /complete for task:', id);

  // PATCH to /complete endpoint - no body needed, backend toggles the status
  return apiClient.patch<Task>(`/api/${userId}/tasks/${id}/complete`, undefined, true);
}

/**
 * Delete a task
 */
export async function deleteTask(id: string): Promise<{ message: string }> {
  const userId = getUserId();
  return apiClient.delete<{ message: string }>(`/api/${userId}/tasks/${id}`, true);
}

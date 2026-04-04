/**
 * Task API Client
 * Feature: 003-frontend-integration (extended: 005-advanced-features-dapr-kafka)
 */

import { apiClient } from './client';
import { Task, CreateTaskData, UpdateTaskData, TaskFilters, TaskListResponse } from '@/types';
import { getUser } from '@/lib/auth/token';

function getUserId(): string {
  const user = getUser();
  if (!user || !user.id) {
    throw new Error('User not authenticated');
  }
  return user.id;
}

/**
 * Build query string from TaskFilters
 */
function buildQueryString(filters?: TaskFilters): string {
  if (!filters) return '';
  const params = new URLSearchParams();
  if (filters.q) params.set('q', filters.q);
  if (filters.priority?.length) {
    filters.priority.forEach((p) => params.append('priority', p));
  }
  if (filters.tags?.length) {
    filters.tags.forEach((t) => params.append('tags', t));
  }
  if (filters.status && filters.status !== 'all') params.set('status', filters.status);
  if (filters.sort_by) params.set('sort_by', filters.sort_by);
  if (filters.sort_order) params.set('sort_order', filters.sort_order);
  if (filters.cursor) params.set('cursor', filters.cursor);
  if (filters.limit) params.set('limit', String(filters.limit));
  const qs = params.toString();
  return qs ? `?${qs}` : '';
}

/**
 * Get tasks with optional filters, search, and pagination
 */
export async function getTasks(filters?: TaskFilters): Promise<TaskListResponse> {
  const userId = getUserId();
  const qs = buildQueryString(filters);
  return apiClient.get<TaskListResponse>(`/api/${userId}/tasks${qs}`, true);
}

/**
 * Create a new task
 */
export async function createTask(data: CreateTaskData): Promise<Task> {
  const userId = getUserId();
  return apiClient.post<Task>(`/api/${userId}/tasks`, data, true);
}

/**
 * Update an existing task (title, description, priority, tags, etc.)
 */
export async function updateTask(id: string, data: UpdateTaskData): Promise<Task> {
  const userId = getUserId();

  // Route completion-only updates through the PATCH /complete toggle endpoint
  if ('is_completed' in data && Object.keys(data).length === 1) {
    return toggleTaskCompletion(id);
  }

  return apiClient.put<Task>(`/api/${userId}/tasks/${id}`, data, true);
}

/**
 * Toggle task completion status via PATCH /complete
 */
export async function toggleTaskCompletion(id: string): Promise<Task> {
  const userId = getUserId();
  return apiClient.patch<Task>(`/api/${userId}/tasks/${id}/complete`, undefined, true);
}

/**
 * Delete a task
 */
export async function deleteTask(id: string): Promise<{ message: string }> {
  const userId = getUserId();
  return apiClient.delete<{ message: string }>(`/api/${userId}/tasks/${id}`, true);
}

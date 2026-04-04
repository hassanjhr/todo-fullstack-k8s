/**
 * Tags API Client
 * Feature: 005-advanced-features-dapr-kafka
 */

import { apiClient } from './client';
import { Tag, TagCreatePayload } from '@/types/tag';
import { getUser } from '@/lib/auth/token';

function getUserId(): string {
  const user = getUser();
  if (!user || !user.id) {
    throw new Error('User not authenticated');
  }
  return user.id;
}

export async function getTags(): Promise<Tag[]> {
  const userId = getUserId();
  const response = await apiClient.get<{ tags: Tag[] }>(`/api/${userId}/tags`, true);
  return response.tags;
}

export async function createTag(payload: TagCreatePayload): Promise<Tag> {
  const userId = getUserId();
  return apiClient.post<Tag>(`/api/${userId}/tags`, payload, true);
}

export async function deleteTag(tagId: string): Promise<void> {
  const userId = getUserId();
  await apiClient.delete<void>(`/api/${userId}/tags/${tagId}`, true);
}

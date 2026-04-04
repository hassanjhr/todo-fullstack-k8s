/**
 * Reminders API Client
 * Feature: 005-advanced-features-dapr-kafka
 */

import { apiClient } from './client';
import { Reminder, ReminderCreatePayload } from '@/types/reminder';
import { getUser } from '@/lib/auth/token';

function getUserId(): string {
  const user = getUser();
  if (!user || !user.id) throw new Error('User not authenticated');
  return user.id;
}

export async function createReminder(
  taskId: string,
  payload: ReminderCreatePayload
): Promise<Reminder> {
  const userId = getUserId();
  return apiClient.post<Reminder>(
    `/api/${userId}/tasks/${taskId}/reminders`,
    payload,
    true
  );
}

export async function deleteReminder(taskId: string, reminderId: string): Promise<void> {
  const userId = getUserId();
  await apiClient.delete<void>(
    `/api/${userId}/tasks/${taskId}/reminders/${reminderId}`,
    true
  );
}

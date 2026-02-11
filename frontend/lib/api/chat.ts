/**
 * Chat API Client
 * Feature: 004-ai-agent-chat
 */

import { apiClient } from './client';
import { ChatResponse, ConversationSummary, ChatMessage } from '@/types';
import { getUser } from '@/lib/auth/token';

function getUserId(): string {
  const user = getUser();
  if (!user || !user.id) {
    throw new Error('User not authenticated');
  }
  return user.id;
}

/**
 * Send a chat message to the AI agent
 */
export async function sendChatMessage(
  message: string,
  conversationId?: string | null
): Promise<ChatResponse> {
  const userId = getUserId();
  return apiClient.post<ChatResponse>(`/api/${userId}/chat`, {
    message,
    conversation_id: conversationId || null,
  });
}

/**
 * Get all conversations for the user
 */
export async function getConversations(): Promise<ConversationSummary[]> {
  const userId = getUserId();
  const response = await apiClient.get<{ conversations: ConversationSummary[] }>(
    `/api/${userId}/conversations`
  );
  return response.conversations;
}

/**
 * Get all messages for a conversation
 */
export async function getMessages(conversationId: string): Promise<ChatMessage[]> {
  const userId = getUserId();
  const response = await apiClient.get<{ conversation_id: string; messages: ChatMessage[] }>(
    `/api/${userId}/conversations/${conversationId}/messages`
  );
  return response.messages;
}

'use client';

import { useEffect, useRef } from 'react';
import { ChatMessage as ChatMessageType } from '@/types';
import ChatMessage from './ChatMessage';

interface ChatThreadProps {
  messages: ChatMessageType[];
  loading?: boolean;
}

export default function ChatThread({ messages, loading = false }: ChatThreadProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  if (messages.length === 0 && !loading) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400 p-8">
        <div className="text-center">
          <div className="text-4xl mb-3">💬</div>
          <div className="text-lg font-medium">Start a conversation</div>
          <div className="text-sm mt-1">
            Ask me to manage your tasks! Try &quot;Show me my tasks&quot; or &quot;Add a task called Buy groceries&quot;
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4">
      {messages.map((msg) => (
        <ChatMessage key={msg.id} message={msg} />
      ))}

      {loading && (
        <div className="flex justify-start mb-4">
          <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 text-gray-500">
            <div className="flex items-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span className="text-sm">AI is thinking...</span>
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}

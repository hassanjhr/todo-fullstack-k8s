'use client';

import { ChatMessage as ChatMessageType, ToolCallInfo } from '@/types';

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[90%] sm:max-w-[80%] rounded-lg px-3 sm:px-4 py-2.5 sm:py-3 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-white border border-gray-200 text-gray-900'
        }`}
      >
        <div className="text-sm font-medium mb-1 opacity-70">
          {isUser ? 'You' : 'AI Assistant'}
        </div>
        <div className="whitespace-pre-wrap">{message.content}</div>

        {/* Tool calls display */}
        {message.tool_calls && message.tool_calls.length > 0 && (
          <div className="mt-3 border-t border-gray-200 pt-2">
            <div className="text-xs font-semibold text-gray-500 mb-1">
              Actions performed:
            </div>
            {message.tool_calls.map((tc: ToolCallInfo, idx: number) => (
              <div
                key={idx}
                className={`text-xs rounded px-2 py-1 mb-1 ${
                  tc.success
                    ? 'bg-green-50 text-green-700 border border-green-200'
                    : 'bg-red-50 text-red-700 border border-red-200'
                }`}
              >
                <span className="font-medium">{tc.tool_name}</span>
                {tc.result && (
                  <span className="ml-1 opacity-80">
                    {tc.success ? ' - Done' : ' - Failed'}
                  </span>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="text-xs opacity-50 mt-1">
          {new Date(message.created_at).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}

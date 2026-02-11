'use client';

import { ConversationSummary } from '@/types';

interface ConversationListProps {
  conversations: ConversationSummary[];
  activeId?: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
  loading?: boolean;
}

export default function ConversationList({
  conversations,
  activeId,
  onSelect,
  onNewChat,
  loading = false,
}: ConversationListProps) {
  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col h-screen md:h-full">
      <div className="p-4 border-b border-gray-700">
        <button
          onClick={onNewChat}
          className="w-full rounded-lg border border-gray-600 px-4 py-2 text-sm font-medium hover:bg-gray-800 transition-colors"
        >
          + New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 text-center text-gray-400 text-sm">Loading...</div>
        ) : conversations.length === 0 ? (
          <div className="p-4 text-center text-gray-400 text-sm">
            No conversations yet
          </div>
        ) : (
          conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => onSelect(conv.id)}
              className={`w-full text-left px-4 py-3 border-b border-gray-800 hover:bg-gray-800 transition-colors ${
                activeId === conv.id ? 'bg-gray-700' : ''
              }`}
            >
              <div className="text-sm font-medium truncate">
                {conv.title || 'New conversation'}
              </div>
              {conv.last_message && (
                <div className="text-xs text-gray-400 truncate mt-1">
                  {conv.last_message}
                </div>
              )}
            </button>
          ))
        )}
      </div>
    </div>
  );
}

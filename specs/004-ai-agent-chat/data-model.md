# Data Model: AI Agent Chat Endpoint

**Branch**: `004-ai-agent-chat` | **Date**: 2026-02-09

## Existing Entities (Unchanged)

### User
- `id`: UUID (PK)
- `email`: string (unique, indexed)
- `hashed_password`: string
- `created_at`: datetime

### Task
- `id`: UUID (PK)
- `user_id`: UUID (FK → users.id, indexed)
- `title`: string (max 200)
- `description`: string? (max 2000)
- `is_completed`: boolean (default false)
- `created_at`: datetime
- `updated_at`: datetime

## New Entities

### Conversation
Represents a chat session belonging to a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, default uuid4 | Unique conversation identifier |
| `user_id` | UUID | FK → users.id, NOT NULL, indexed | Owner of this conversation |
| `title` | string? | max 200, nullable | Auto-generated from first message |
| `created_at` | datetime | NOT NULL, default now | Conversation creation timestamp |
| `updated_at` | datetime | NOT NULL, default now | Last activity timestamp |

**Indexes**:
- `idx_conversation_user_id`: Fast lookup by user
- `idx_conversation_user_updated`: User's conversations sorted by recent activity

**Relationships**:
- Conversation belongs to User (N:1)
- Conversation has many Messages (1:N)

### Message
Represents a single message within a conversation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, default uuid4 | Unique message identifier |
| `conversation_id` | UUID | FK → conversations.id, NOT NULL, indexed | Parent conversation |
| `role` | string | NOT NULL, enum: "user"/"assistant"/"system" | Message sender role |
| `content` | text | NOT NULL | Message text content |
| `tool_calls` | JSON? | nullable | Tool invocations (assistant messages only) |
| `created_at` | datetime | NOT NULL, default now | Message creation timestamp |

**Indexes**:
- `idx_message_conversation_id`: Fast lookup by conversation
- `idx_message_conversation_created`: Messages in chronological order

**Relationships**:
- Message belongs to Conversation (N:1)

**Cascade**: When a Conversation is deleted, all its Messages are deleted (ON DELETE CASCADE).

## Entity Relationship Diagram

```
┌──────────┐       ┌──────────────┐       ┌──────────┐
│   User   │──1:N──│ Conversation │──1:N──│ Message  │
│          │       │              │       │          │
│ id (PK)  │       │ id (PK)      │       │ id (PK)  │
│ email    │       │ user_id (FK) │       │ conv_id  │
│ password │       │ title        │       │ role     │
│ created  │       │ created_at   │       │ content  │
└──────────┘       │ updated_at   │       │ tools    │
      │            └──────────────┘       │ created  │
      │                                    └──────────┘
      │            ┌──────────┐
      └─────1:N────│   Task   │
                   │          │
                   │ id (PK)  │
                   │ user_id  │
                   │ title    │
                   │ ...      │
                   └──────────┘
```

## State Transitions

### Conversation
- Created → Active (first message sent)
- Active → Active (subsequent messages)
- No explicit "closed" state in MVP

### Message
- Messages are immutable once created (append-only log)
- No updates or deletions of individual messages in MVP

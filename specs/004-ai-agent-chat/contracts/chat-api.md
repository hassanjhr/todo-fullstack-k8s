# API Contracts: AI Agent Chat Endpoint

**Branch**: `004-ai-agent-chat` | **Date**: 2026-02-09

## POST /api/{user_id}/chat

Send a message to the AI agent and receive a response.

**Authentication**: Required (JWT Bearer token)
**Authorization**: user_id in URL MUST match authenticated user

### Request

```json
{
  "message": "Add a task called Buy groceries",
  "conversation_id": "optional-uuid-or-null"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | User's natural-language message (1–2000 chars) |
| `conversation_id` | UUID? | No | Existing conversation to continue. If null/omitted, creates new conversation |

### Response (200 OK)

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440099",
  "response": "I've created a new task called 'Buy groceries' for you!",
  "tool_calls": [
    {
      "tool_name": "create_task",
      "parameters": {
        "title": "Buy groceries",
        "description": null
      },
      "result": {
        "task_id": "660e8400-e29b-41d4-a716-446655440001",
        "title": "Buy groceries",
        "is_completed": false
      },
      "success": true
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `conversation_id` | UUID | Conversation ID (new or existing) |
| `response` | string | Agent's natural-language response |
| `tool_calls` | array | List of MCP tool invocations made by the agent |
| `tool_calls[].tool_name` | string | Name of the MCP tool invoked |
| `tool_calls[].parameters` | object | Parameters passed to the tool |
| `tool_calls[].result` | object | Tool execution result |
| `tool_calls[].success` | boolean | Whether the tool call succeeded |

### Error Responses

| Status | Condition |
|--------|-----------|
| 401 | Missing or invalid JWT token |
| 403 | user_id does not match authenticated user |
| 422 | Empty message or invalid conversation_id |
| 503 | OpenAI API unavailable or timeout |

---

## GET /api/{user_id}/conversations

List user's conversations with last message preview.

**Authentication**: Required (JWT Bearer token)

### Response (200 OK)

```json
{
  "conversations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440099",
      "title": "Task management",
      "last_message": "I've created a new task called 'Buy groceries'...",
      "created_at": "2026-02-09T10:00:00Z",
      "updated_at": "2026-02-09T10:05:00Z"
    }
  ]
}
```

### Error Responses

| Status | Condition |
|--------|-----------|
| 401 | Missing or invalid JWT token |
| 403 | user_id does not match authenticated user |

---

## GET /api/{user_id}/conversations/{conversation_id}/messages

Retrieve all messages for a conversation.

**Authentication**: Required (JWT Bearer token)

### Response (200 OK)

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440099",
  "messages": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440001",
      "role": "user",
      "content": "Add a task called Buy groceries",
      "tool_calls": null,
      "created_at": "2026-02-09T10:00:00Z"
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "role": "assistant",
      "content": "I've created a new task called 'Buy groceries' for you!",
      "tool_calls": [
        {
          "tool_name": "create_task",
          "parameters": {"title": "Buy groceries"},
          "result": {"task_id": "...", "title": "Buy groceries"},
          "success": true
        }
      ],
      "created_at": "2026-02-09T10:00:05Z"
    }
  ]
}
```

### Error Responses

| Status | Condition |
|--------|-----------|
| 401 | Missing or invalid JWT token |
| 403 | user_id does not match authenticated user, or conversation belongs to another user |
| 404 | Conversation not found |

# Feature Specification: AI Agent Chat Endpoint

**Feature Branch**: `004-ai-agent-chat`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "AI Agent Chat Endpoint with OpenAI Agents SDK, MCP tools, conversation persistence, and stateless request cycle"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Send a Chat Message to Manage Todos (Priority: P1)

An authenticated user opens the chat interface and types a natural-language message such as "Add a task called Buy groceries" or "Show me my tasks." The system processes the message through an AI agent that understands the intent, invokes the appropriate MCP tool(s) to perform the action, and returns a conversational response along with details of what was done.

**Why this priority**: This is the core value proposition — without the ability to send a message and get an AI-driven response that actually mutates or reads tasks, the entire feature has no function.

**Independent Test**: Can be fully tested by sending a POST request with a user message and verifying the response contains a conversation_id, a natural-language response, and tool_calls array reflecting the action taken.

**Acceptance Scenarios**:

1. **Given** an authenticated user with no existing conversations, **When** the user sends "Add a task called Buy groceries", **Then** the system creates a new conversation, stores the user message, invokes the create-task MCP tool, stores the assistant response, and returns `{conversation_id, response, tool_calls}` where tool_calls includes the create-task invocation.
2. **Given** an authenticated user, **When** the user sends "Show me all my tasks", **Then** the system invokes the list-tasks MCP tool, returns a response summarizing the user's tasks, and tool_calls reflects the list-tasks invocation.
3. **Given** an authenticated user, **When** the user sends a message without a valid JWT token, **Then** the system returns 401 Unauthorized without processing any agent logic.

---

### User Story 2 - Continue an Existing Conversation (Priority: P2)

An authenticated user returns to a previous conversation and sends a follow-up message. The system loads the full conversation history from the database, reconstructs the agent context, and provides a contextually aware response that references prior messages.

**Why this priority**: Conversation continuity is essential for a natural chat experience. Without it, each message is isolated and the agent cannot reference prior context.

**Independent Test**: Can be tested by sending two messages in the same conversation_id and verifying the second response demonstrates awareness of the first message's context.

**Acceptance Scenarios**:

1. **Given** a user with an existing conversation containing the message "Add a task called Buy groceries" and the assistant's confirmation, **When** the user sends "Mark it as complete" in the same conversation, **Then** the agent understands "it" refers to "Buy groceries" and invokes the update-task MCP tool to toggle completion.
2. **Given** a user with an existing conversation, **When** the user sends a follow-up message, **Then** the full conversation history is loaded from the database and passed to the agent as context.
3. **Given** a user providing a conversation_id that belongs to another user, **Then** the system returns 403 Forbidden.

---

### User Story 3 - View Conversation History (Priority: P3)

An authenticated user wants to see their past conversations and the messages within them. The system provides endpoints to list conversations and retrieve messages for a specific conversation.

**Why this priority**: While not essential for the core chat flow, viewing history enables users to review past interactions and pick up where they left off.

**Independent Test**: Can be tested by creating conversations via chat, then retrieving the list and verifying all messages are present with correct roles and timestamps.

**Acceptance Scenarios**:

1. **Given** a user with three past conversations, **When** the user requests their conversation list, **Then** the system returns all three conversations with their IDs, creation dates, and last message previews.
2. **Given** a user requesting messages for a specific conversation_id, **Then** the system returns all messages in chronological order with role (user/assistant), content, and timestamps.
3. **Given** a user requesting a conversation belonging to another user, **Then** the system returns 403 Forbidden.

---

### User Story 4 - Chat UI Integration (Priority: P4)

An authenticated user interacts with a chat interface on the frontend that sends messages to the backend chat endpoint and displays responses in real-time. The UI shows a message input, conversation thread, and indicates when the AI is processing.

**Why this priority**: The frontend integration delivers the complete user experience but depends on the backend being functional first.

**Independent Test**: Can be tested by opening the chat page, typing a message, and verifying the response appears in the conversation thread with proper formatting.

**Acceptance Scenarios**:

1. **Given** the user is on the chat page, **When** they type a message and press send, **Then** the message appears in the thread, a loading indicator shows, and the assistant response appears when ready.
2. **Given** the user has multiple conversations, **When** they navigate to the chat page, **Then** they can see a list of past conversations and select one to continue.
3. **Given** the agent performs a task action (create, update, delete), **When** the response arrives, **Then** the UI displays both the conversational response and a summary of the tool actions taken.

---

### Edge Cases

- What happens when the AI agent fails to invoke any MCP tool (e.g., ambiguous message like "hello")? The agent MUST still return a conversational response without tool_calls.
- What happens when an MCP tool invocation fails (e.g., task not found for update)? The agent MUST return an error explanation in the response and the tool_calls array MUST include the failed invocation with error details.
- What happens when the conversation history is very long (100+ messages)? The system MUST handle context window limits by truncating older messages while preserving the most recent context.
- What happens when the OpenAI API is unavailable or times out? The system MUST return a 503 Service Unavailable with a user-friendly error message.
- What happens when a user sends an empty message? The system MUST return 422 Unprocessable Entity.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a user message via a chat endpoint and return an AI-generated response with conversation_id, response text, and tool_calls array
- **FR-002**: System MUST create a new conversation automatically when no conversation_id is provided in the request
- **FR-003**: System MUST load full conversation history from the database when a conversation_id is provided
- **FR-004**: System MUST store the user message in the database before processing it through the agent
- **FR-005**: System MUST store the assistant response and tool call details in the database before returning to the client
- **FR-006**: System MUST invoke MCP tools for all task operations (create, read, update, delete, toggle completion)
- **FR-007**: System MUST reconstruct agent context from stored messages on every request (stateless backend)
- **FR-008**: System MUST support listing a user's conversations with last message preview
- **FR-009**: System MUST support retrieving all messages for a specific conversation in chronological order
- **FR-010**: System MUST provide a chat UI page on the frontend that integrates with the chat endpoint
- **FR-011**: System MUST display a loading state in the UI while the agent is processing
- **FR-012**: System MUST display tool actions taken by the agent alongside the conversational response

### Security Requirements *(mandatory)*

- **SR-001**: All chat endpoints MUST require valid JWT authentication
- **SR-002**: User identity MUST be extracted from JWT token, not request body
- **SR-003**: All database queries MUST filter by authenticated user_id
- **SR-004**: Unauthorized requests MUST return 401 status code
- **SR-005**: Authorization failures (accessing another user's conversation) MUST return 403 status code
- **SR-006**: MCP tools MUST validate user ownership of target resources before executing mutations
- **SR-007**: The agent MUST NOT be able to override or fabricate the authenticated user_id
- **SR-008**: All agent tool invocations MUST be logged with user_id, tool name, and parameters

### Key Entities

- **Conversation**: Represents a chat session belonging to a user. Key attributes: unique identifier, owner (user_id), creation timestamp, last activity timestamp.
- **Message**: Represents a single message within a conversation. Key attributes: unique identifier, conversation reference, role (user or assistant), content text, tool_calls data (for assistant messages), creation timestamp.
- **MCP Tool Call**: Represents a record of a tool invocation by the agent. Key attributes: tool name, input parameters, output result, success/failure status, associated message reference.

## Assumptions

- The existing Task and User models from Phase II remain unchanged; the chat feature adds new entities (Conversation, Message) alongside them.
- The OpenAI Agents SDK is used for agent orchestration; the specific OpenAI model (e.g., GPT-4o) will be configurable via environment variable.
- MCP tools wrap the existing task CRUD operations already implemented in the backend.
- A single conversation can span multiple sessions; users can return to any past conversation.
- Message truncation strategy for long conversations: keep the system prompt + last N messages that fit within the model's context window.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can send a natural-language message and receive an AI response that correctly performs the requested task action within 10 seconds
- **SC-002**: Conversation context is maintained across multiple messages — the agent correctly resolves references to prior messages (e.g., "mark it as done" after adding a task)
- **SC-003**: All task mutations performed through chat are reflected in the existing task list (data consistency between chat and direct API)
- **SC-004**: 100% of agent tool invocations are logged with user identity and can be audited
- **SC-005**: No cross-user data leakage — users cannot access or modify another user's conversations or tasks through the chat interface
- **SC-006**: The chat UI provides a responsive experience with visible loading states and clear display of both conversational responses and tool actions

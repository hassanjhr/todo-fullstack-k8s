# Tasks: AI Agent Chat Endpoint

**Input**: Design documents from `/specs/004-ai-agent-chat/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/chat-api.md
**Branch**: `004-ai-agent-chat` | **Date**: 2026-02-09

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add new dependencies and environment configuration required for AI agent chat feature

- [x] T001 Add `openai-agents` to `backend/requirements.txt`
- [x] T002 [P] Add `OPENAI_API_KEY` and `OPENAI_MODEL` settings to `backend/src/config.py` (extend existing `Settings` class)
- [x] T003 [P] Add `OPENAI_API_KEY` and `OPENAI_MODEL` to `backend/.env` (with placeholder values)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database models and schemas that MUST be complete before ANY user story can be implemented

**Agent**: `neon-db-manager`

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [P] Create Conversation SQLModel in `backend/src/models/conversation.py` with fields: id (UUID PK), user_id (FK → users.id, indexed), title (str?, max 200), created_at, updated_at. Include indexes: idx_conversation_user_id, idx_conversation_user_updated
- [x] T005 [P] Create Message SQLModel in `backend/src/models/message.py` with fields: id (UUID PK), conversation_id (FK → conversations.id, indexed, ON DELETE CASCADE), role (str, enum: user/assistant/system), content (text), tool_calls (JSON?), created_at. Include indexes: idx_message_conversation_id, idx_message_conversation_created
- [x] T006 Export new models from `backend/src/models/__init__.py` (import Conversation, Message)
- [x] T007 Create chat Pydantic schemas in `backend/src/schemas/chat.py`: ChatRequest (message: str, conversation_id: UUID?), ChatResponse (conversation_id: UUID, response: str, tool_calls: list), ToolCallInfo (tool_name: str, parameters: dict, result: dict, success: bool), ConversationSummary (id, title, last_message, created_at, updated_at), MessageOut (id, role, content, tool_calls, created_at)
- [x] T008 Run table creation for conversations and messages tables on Neon PostgreSQL (use `SQLModel.metadata.create_all` in `backend/src/database.py` or migration script)

**Checkpoint**: Database tables exist and schemas are defined — user story implementation can begin

---

## Phase 3: User Story 1 — Send a Chat Message to Manage Todos (Priority: P1) MVP

**Goal**: An authenticated user sends a natural-language message via POST /api/{user_id}/chat and receives an AI response with tool_calls reflecting task actions performed

**Independent Test**: Send POST /api/{user_id}/chat with `{"message": "Add a task called Buy groceries"}` → verify response contains conversation_id, response text, and tool_calls with create_task invocation

**Agent**: `fastapi-backend-dev`

### Implementation for User Story 1

- [x] T009 Create agent package `backend/src/agent/__init__.py` (empty init)
- [x] T010 [P] [US1] Implement 6 MCP tool functions in `backend/src/agent/tools.py`:
  - `create_task(user_id, title, description?)` → wraps task creation via SQLModel
  - `list_tasks(user_id)` → wraps task listing
  - `get_task(user_id, task_id)` → wraps single task retrieval
  - `update_task(user_id, task_id, title?, description?)` → wraps task update
  - `delete_task(user_id, task_id)` → wraps task deletion
  - `toggle_task(user_id, task_id)` → wraps task completion toggle
  - Each tool: validates user ownership, returns structured result, handles errors
  - Each tool receives an async database session internally
- [x] T011 [US1] Define agent with system prompt and tools in `backend/src/agent/agent.py`:
  - System prompt: "You are a helpful todo management assistant..."
  - Register all 6 MCP tools from tools.py
  - Configure model from `settings.OPENAI_MODEL` (default: gpt-4o)
- [x] T012 [US1] Implement stateless agent runner in `backend/src/agent/runner.py`:
  - `run_chat(user_id, message, conversation_id?, session)` function
  - Step 1: Load or create conversation
  - Step 2: Store user message in DB
  - Step 3: Reconstruct message history from DB (all messages for conversation, ordered by created_at)
  - Step 4: Call `Runner.run(agent, messages)` with reconstructed context
  - Step 5: Extract response text and tool_calls from RunResult
  - Step 6: Store assistant message (with tool_calls JSON) in DB
  - Step 7: Update conversation.updated_at and auto-generate title from first message
  - Step 8: Return ChatResponse
- [x] T013 [US1] Create chat API route in `backend/src/api/routes/chat.py`:
  - `POST /api/{user_id}/chat` endpoint
  - Dependencies: `get_current_user`, `verify_user_access`, `get_session`
  - Request body: ChatRequest schema
  - Response: ChatResponse schema
  - Error handling: 401 (no auth), 403 (wrong user), 422 (empty message), 503 (OpenAI unavailable)
- [x] T014 [US1] Register chat router in `backend/src/main.py`:
  - Import and include chat router with prefix `/api`
  - Ensure CORS settings allow chat endpoint access

**Checkpoint**: User Story 1 complete — can send a chat message and receive AI response with tool invocations

---

## Phase 4: User Story 2 — Continue an Existing Conversation (Priority: P2)

**Goal**: User sends follow-up messages in an existing conversation; agent has full context from prior messages and responds contextually

**Independent Test**: Send two messages in same conversation_id — second message references first ("Mark it as complete" after creating a task) and agent correctly resolves the reference

**Agent**: `fastapi-backend-dev`

### Implementation for User Story 2

- [x] T015 [US2] Enhance runner in `backend/src/agent/runner.py` to handle context reconstruction:
  - When conversation_id is provided: load all messages, verify conversation belongs to user (403 if not)
  - Implement context window management: if messages exceed 50, truncate to system prompt + last 50 messages
  - Ensure tool_calls from prior assistant messages are included in reconstructed context
- [x] T016 [US2] Add conversation ownership validation in `backend/src/api/routes/chat.py`:
  - Verify conversation_id belongs to authenticated user before processing
  - Return 403 if conversation belongs to another user

**Checkpoint**: User Story 2 complete — multi-turn conversations work with full context awareness

---

## Phase 5: User Story 3 — View Conversation History (Priority: P3)

**Goal**: User can list their conversations and retrieve messages for any conversation

**Independent Test**: Create conversations via chat, then GET /conversations to verify list, GET /conversations/{id}/messages to verify message retrieval

**Agent**: `fastapi-backend-dev`

### Implementation for User Story 3

- [x] T017 [P] [US3] Implement GET /api/{user_id}/conversations endpoint in `backend/src/api/routes/chat.py`:
  - Query conversations where user_id matches authenticated user
  - Order by updated_at DESC
  - Include last message preview (first 100 chars of most recent message content)
  - Response: list of ConversationSummary
- [x] T018 [P] [US3] Implement GET /api/{user_id}/conversations/{conversation_id}/messages endpoint in `backend/src/api/routes/chat.py`:
  - Verify conversation belongs to authenticated user (403 if not)
  - Return 404 if conversation not found
  - Query messages ordered by created_at ASC
  - Response: conversation_id + list of MessageOut

**Checkpoint**: User Story 3 complete — can browse conversation history and read past messages

---

## Phase 6: User Story 4 — Chat UI Integration (Priority: P4)

**Goal**: Frontend chat page at /dashboard/chat with message input, conversation thread, conversation sidebar, and loading states

**Independent Test**: Open /dashboard/chat, type a message, verify response appears in thread with tool action summaries

**Agent**: `nextjs-ui-builder`

### Implementation for User Story 4

- [x] T019 [US4] Add chat-related TypeScript types to `frontend/types/index.ts`:
  - ChatRequest, ChatResponse, ToolCallInfo, ConversationSummary, MessageOut interfaces
- [x] T020 [US4] Create chat API client functions in `frontend/lib/api/chat.ts`:
  - `sendMessage(userId, message, conversationId?)` → POST /api/{user_id}/chat
  - `getConversations(userId)` → GET /api/{user_id}/conversations
  - `getMessages(userId, conversationId)` → GET /api/{user_id}/conversations/{id}/messages
  - Uses existing `apiClient` singleton for JWT injection
- [x] T021 [P] [US4] Create ChatMessage component in `frontend/components/chat/ChatMessage.tsx`:
  - Renders single message with role indicator (user/assistant)
  - Displays tool call summaries for assistant messages (tool name + result)
  - Timestamps
- [x] T022 [P] [US4] Create ChatInput component in `frontend/components/chat/ChatInput.tsx`:
  - Text input with send button
  - Disabled state while loading
  - Submit on Enter key
- [x] T023 [US4] Create ChatThread component in `frontend/components/chat/ChatThread.tsx`:
  - Renders list of ChatMessage components
  - Auto-scrolls to latest message
  - Shows loading indicator while agent is processing
- [x] T024 [US4] Create ConversationList component in `frontend/components/chat/ConversationList.tsx`:
  - Sidebar listing past conversations
  - Shows title and last message preview
  - Click to load conversation messages
  - "New Chat" button to start fresh conversation
- [x] T025 [US4] Create chat page in `frontend/app/dashboard/chat/page.tsx`:
  - Layout: ConversationList sidebar + ChatThread + ChatInput
  - Uses `useAuth` hook for authentication (redirect if not logged in)
  - State management: active conversation, messages, loading state
  - Integrates all chat components and API client
  - Responsive design (sidebar collapses on mobile)
- [x] T026 [US4] Add chat navigation link to existing dashboard layout/navigation:
  - Add "Chat" link to dashboard sidebar/navigation pointing to `/dashboard/chat`

**Checkpoint**: User Story 4 complete — full chat UI functional with conversation management

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end validation and refinement across all stories

- [ ] T027 (manual validation needed) Verify end-to-end flow: sign in → open chat → send message → see AI response with tool actions → verify task created in task list page
- [x] T028 [P] Verify CORS configuration in `backend/src/main.py` allows chat endpoint access from frontend origin
- [ ] T029 (manual validation needed) [P] Verify error handling: test 401 (no token), 403 (wrong user), 422 (empty message), 503 (bad API key) responses
- [ ] T030 (manual validation needed) Run quickstart.md validation steps to confirm setup guide accuracy

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on T001 (openai-agents installed) — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 completion — core MVP
- **US2 (Phase 4)**: Depends on Phase 3 (T012 runner must exist to enhance)
- **US3 (Phase 5)**: Depends on Phase 2 — can run in parallel with US1/US2
- **US4 (Phase 6)**: Depends on Phase 3 (backend endpoints must exist for frontend to call)
- **Polish (Phase 7)**: Depends on all user stories complete

### Critical Path

```
T001 → T004/T005/T007 → T010/T011 → T012 → T013/T014 → T015/T016 → T025
 Setup    DB Models       MCP Tools   Runner    Endpoint     Context    Frontend
```

### Parallel Opportunities

- T002, T003 can run in parallel with T001
- T004, T005, T007 can run in parallel (different files)
- T017, T018 can run in parallel (different endpoints, same file but independent functions)
- T021, T022 can run in parallel (different components)
- US3 (Phase 5) can run in parallel with US1 (Phase 3) after Phase 2

### Agent Assignment

| Phase | Agent | Tasks |
|-------|-------|-------|
| Phase 1: Setup | `fastapi-backend-dev` | T001–T003 |
| Phase 2: Foundational | `neon-db-manager` | T004–T008 |
| Phase 3: US1 (Chat) | `fastapi-backend-dev` | T009–T014 |
| Phase 4: US2 (Context) | `fastapi-backend-dev` | T015–T016 |
| Phase 5: US3 (History) | `fastapi-backend-dev` | T017–T018 |
| Phase 6: US4 (Frontend) | `nextjs-ui-builder` | T019–T026 |
| Phase 7: Polish | Manual/All | T027–T030 |

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1: Setup (T001–T003)
2. Complete Phase 2: Foundational (T004–T008)
3. Complete Phase 3: User Story 1 (T009–T014)
4. **STOP and VALIDATE**: Test via curl — POST /chat with a message
5. Deploy backend if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test POST /chat → MVP backend working
3. Add US2 → Test multi-turn conversations → Context-aware
4. Add US3 → Test GET endpoints → History browsable
5. Add US4 → Test chat UI → Full user experience
6. Polish → End-to-end validation → Production ready

---

## Notes

- All backend tasks use async SQLModel with Neon PostgreSQL
- MCP tools in T010 must NOT access the database directly from the agent — they wrap existing CRUD patterns
- Runner (T012) is the integration point: UI → Runner → Agent → MCP Tools → Database
- Frontend tasks (T019–T026) follow existing patterns from dashboard page
- No test tasks included (not requested in spec)
- Total tasks: 30

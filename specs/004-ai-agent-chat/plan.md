# Implementation Plan: AI Agent Chat Endpoint

**Branch**: `004-ai-agent-chat` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-ai-agent-chat/spec.md`

## Summary

Implement an AI-powered chat endpoint that allows users to manage their todos through natural language. The system uses the OpenAI Agents SDK to orchestrate an AI agent that invokes MCP tools (wrapping existing task CRUD operations) to perform actions. All conversations and messages are persisted to the database. The backend remains fully stateless — conversation context is reconstructed from stored messages on every request. A chat UI page is added to the Next.js frontend.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript (frontend)
**Primary Dependencies**: FastAPI, OpenAI Agents SDK (`openai-agents`), SQLModel, Next.js 16+
**Storage**: Neon Serverless PostgreSQL (existing) — new tables: `conversations`, `messages`
**Testing**: Manual API testing via curl/docs, frontend manual testing
**Target Platform**: Linux server (backend on HF Spaces), Vercel (frontend)
**Project Type**: Web application (separate frontend + backend)
**Performance Goals**: Chat response within 10 seconds (includes OpenAI API latency)
**Constraints**: Stateless backend, MCP-only tool access, user data isolation
**Scale/Scope**: Single-user concurrent, MVP for demo

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Spec-First Development**
- [x] Feature has complete spec.md with acceptance criteria, API contracts, and data models
- [x] No implementation has begun before spec approval

**II. Security by Default**
- [x] All API endpoints will require JWT authentication
- [x] JWT verification strategy documented (reuse existing `get_current_user` dependency)
- [x] User identity extraction from JWT (not request body) confirmed
- [x] User data isolation strategy defined (MCP tools receive user_id from JWT, not agent)

**III. User Data Isolation**
- [x] Database models include user_id foreign keys (conversations.user_id)
- [x] Query filtering by authenticated user_id documented (all MCP tools filter by user_id)
- [x] No cross-user data access paths identified (conversation ownership verified)

**IV. Reproducibility**
- [x] Plan references spec.md and will generate tasks.md
- [x] Significant architectural decisions identified for ADR documentation
- [x] Implementation will be traceable through PHRs

**V. Automation-First**
- [x] Appropriate Claude Code agents identified for each domain:
  - `neon-db-manager` for database schema (conversations, messages tables)
  - `fastapi-backend-dev` for chat endpoint, MCP tools, agent runner
  - `nextjs-ui-builder` for chat UI page
- [x] No manual coding planned

**VI. Production Realism**
- [x] Using Neon PostgreSQL (not in-memory/SQLite)
- [x] Using Better Auth with JWT (not hardcoded users)
- [x] Using FastAPI with REST conventions (not mock endpoints)
- [x] Using Next.js 16+ App Router (not static HTML)
- [x] Proper error handling with HTTP status codes planned (401, 403, 422, 503)
- [x] Environment-based configuration (.env) planned (OPENAI_API_KEY, OPENAI_MODEL)

**VII. Agent-First Architecture**
- [x] AI agent is sole entry point for chat-driven task operations
- [x] Agent uses OpenAI Agents SDK for orchestration
- [x] Agent does NOT access database directly — all via MCP tools
- [x] System separation: UI → Agent Runner → MCP Tools → Database

**VIII. MCP Tool Exclusivity**
- [x] All task operations exposed as named MCP tools (6 tools)
- [x] MCP tools are stateless, deterministic, independently testable
- [x] Each tool validates user ownership before executing
- [x] Tool inputs/outputs have defined schemas
- [x] All tool invocations logged with user_id

**IX. Stateless Backend with Context Reconstruction**
- [x] No in-memory conversation state between requests
- [x] Conversation history loaded from database on each request
- [x] Agent runner receives full reconstructed context
- [x] No server-side session objects

**X. Conversation Persistence**
- [x] User message stored before agent processes it
- [x] Assistant response stored before returning to client
- [x] Messages include user_id, conversation_id, role, content, created_at
- [x] Persistence failure prevents response from being returned

## Project Structure

### Documentation (this feature)

```text
specs/004-ai-agent-chat/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 research output
├── data-model.md        # Entity definitions
├── quickstart.md        # Setup and verification guide
├── contracts/
│   └── chat-api.md      # API endpoint contracts
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (new files)

```text
backend/
├── src/
│   ├── models/
│   │   ├── conversation.py   # NEW: Conversation SQLModel
│   │   └── message.py        # NEW: Message SQLModel
│   ├── schemas/
│   │   └── chat.py           # NEW: Chat request/response Pydantic models
│   ├── api/routes/
│   │   └── chat.py           # NEW: Chat endpoint routes
│   ├── agent/
│   │   ├── __init__.py       # NEW: Agent package
│   │   ├── tools.py          # NEW: MCP tool functions (6 tools)
│   │   ├── agent.py          # NEW: Agent definition with system prompt
│   │   └── runner.py         # NEW: Agent runner (context reconstruction + execution)
│   ├── config.py             # MODIFIED: Add OPENAI_API_KEY, OPENAI_MODEL
│   └── main.py               # MODIFIED: Register chat router
├── requirements.txt          # MODIFIED: Add openai-agents

frontend/
├── app/
│   └── dashboard/
│       └── chat/
│           └── page.tsx      # NEW: Chat UI page
├── components/
│   └── chat/
│       ├── ChatMessage.tsx   # NEW: Single message component
│       ├── ChatInput.tsx     # NEW: Message input component
│       ├── ChatThread.tsx    # NEW: Message thread component
│       └── ConversationList.tsx # NEW: Sidebar conversation list
├── lib/
│   └── api/
│       └── chat.ts           # NEW: Chat API client functions
└── types/
    └── index.ts              # MODIFIED: Add chat-related types
```

**Structure Decision**: Web application with separate frontend/backend. New chat feature adds to existing `backend/src/` and `frontend/` directories. Agent code isolated in `backend/src/agent/` package to enforce separation from direct database access in routes.

## Complexity Tracking

No Constitution Check violations. All 10 principles satisfied.

## Implementation Phases

### Phase 1: Database Models (Foundation)
- Add Conversation and Message SQLModel tables
- Create database migration
- Agent: `neon-db-manager`

### Phase 2: MCP Tools
- Implement 6 MCP tool functions wrapping existing task CRUD
- Each tool receives user_id, validates ownership, returns structured result
- Agent: `fastapi-backend-dev`

### Phase 3: Agent Definition + Runner
- Define agent with system prompt and MCP tools
- Implement stateless runner (load history → build messages → run agent → extract result)
- Add OPENAI_API_KEY to config
- Agent: `fastapi-backend-dev`

### Phase 4: Chat API Endpoint
- POST /api/{user_id}/chat (main chat endpoint)
- GET /api/{user_id}/conversations (list conversations)
- GET /api/{user_id}/conversations/{id}/messages (get messages)
- Pydantic schemas for request/response
- Register router in main.py
- Agent: `fastapi-backend-dev`

### Phase 5: Frontend Chat UI
- Chat page at /dashboard/chat
- Chat input, message thread, conversation sidebar
- API client functions for chat endpoints
- Agent: `nextjs-ui-builder`

### Phase 6: Integration + Polish
- End-to-end testing
- Error handling refinement
- CORS configuration update if needed

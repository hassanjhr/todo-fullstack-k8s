# Research: AI Agent Chat Endpoint

**Branch**: `004-ai-agent-chat` | **Date**: 2026-02-09

## R1: OpenAI Agents SDK Integration Pattern

**Decision**: Use `openai-agents` Python SDK with `Runner.run()` for stateless per-request agent invocation.

**Rationale**: The OpenAI Agents SDK provides a high-level abstraction for agent orchestration with built-in tool calling, context management, and structured output. Using `Runner.run()` (not streaming) keeps the first implementation simple while allowing migration to `Runner.run_streamed()` later.

**Alternatives considered**:
- **LangChain**: Heavier dependency, more abstraction layers than needed. Rejected for simplicity.
- **Custom agent loop**: Manual tool-calling loop with raw OpenAI API. Rejected because Agents SDK handles tool dispatch, retries, and structured output natively.
- **CrewAI**: Multi-agent framework, overkill for single-agent todo management. Rejected.

**Key implementation details**:
- Install: `openai-agents` (pip package)
- Agent defined with system prompt + MCP tools
- `Runner.run(agent, messages)` accepts reconstructed conversation history
- Tool results are automatically fed back to the agent by the SDK
- Agent returns structured `RunResult` with messages and tool calls

## R2: MCP Server Architecture for Todo Tools

**Decision**: Implement MCP tools as Python functions registered with the agent via the OpenAI Agents SDK `function_tool` decorator. Each tool wraps existing SQLModel CRUD operations.

**Rationale**: The Agents SDK supports defining tools as Python functions with type-annotated parameters. This maps directly to MCP tool semantics: each function is stateless, receives user_id as a parameter, validates ownership, and returns structured results.

**Alternatives considered**:
- **Separate MCP server process**: Run tools as a standalone MCP server connected via stdio/SSE. Rejected for Phase-III MVP — adds deployment complexity. Can be extracted later.
- **Direct database access from agent**: Violates Constitution Principle VIII (MCP Tool Exclusivity). Rejected.

**MCP Tools to implement**:
| Tool Name | Operation | Parameters |
|-----------|-----------|------------|
| `create_task` | Create new task | user_id, title, description? |
| `list_tasks` | List user's tasks | user_id |
| `get_task` | Get single task | user_id, task_id |
| `update_task` | Update task | user_id, task_id, title, description? |
| `delete_task` | Delete task | user_id, task_id |
| `toggle_task` | Toggle completion | user_id, task_id |

## R3: Conversation Persistence Strategy

**Decision**: Two new SQLModel tables: `conversations` and `messages`. Messages store role, content, and optional tool_calls JSON. Context reconstructed by loading all messages for a conversation ordered by created_at.

**Rationale**: Simple relational model that maps directly to the OpenAI message format. Storing tool_calls as JSON in the message record keeps the schema simple while preserving full audit trail.

**Alternatives considered**:
- **Single messages table without conversations**: Loses the ability to group messages into sessions. Rejected.
- **Redis for conversation state**: Violates Constitution Principle IX (stateless backend, persistent storage required). Rejected.
- **Store full agent context blob**: Opaque, not queryable, harder to truncate. Rejected.

## R4: Stateless Request Cycle

**Decision**: Each POST /chat request: (1) authenticate, (2) load/create conversation, (3) store user message, (4) reconstruct message history, (5) run agent, (6) store assistant response, (7) return result.

**Rationale**: This 7-step cycle ensures full statelessness — no server-side memory between requests. Every piece of state is in the database. Crash-safe by design.

**Context window management**: For long conversations (100+ messages), truncate to system prompt + last 50 messages. This fits within GPT-4o's context window while preserving recent context.

## R5: Frontend Chat UI Pattern

**Decision**: New `/dashboard/chat` page with a conversation sidebar and message thread. Uses existing `apiClient` for HTTP requests and existing auth context for JWT tokens.

**Rationale**: Builds on existing frontend patterns (apiClient, useAuth, component structure). Chat page added alongside existing dashboard, not replacing it.

**Alternatives considered**:
- **Replace dashboard with chat**: Loses direct task management UI. Rejected — both should coexist.
- **Separate chat app**: Unnecessary complexity for MVP. Rejected.
- **WebSocket/SSE streaming**: Adds complexity for MVP. Can be added in future iteration. Rejected for now.

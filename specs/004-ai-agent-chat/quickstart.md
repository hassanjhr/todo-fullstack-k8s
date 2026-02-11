# Quickstart: AI Agent Chat Endpoint

**Branch**: `004-ai-agent-chat` | **Date**: 2026-02-09

## Prerequisites

- Python 3.11+ with virtual environment
- Node.js 18+ with npm
- Neon PostgreSQL database (existing from Phase II)
- OpenAI API key

## Backend Setup

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install openai-agents

# Add to .env
echo "OPENAI_API_KEY=your-openai-api-key-here" >> .env
echo "OPENAI_MODEL=gpt-4o" >> .env

# Run database migration for new tables (conversations, messages)
# (migration script to be created during implementation)
python -m scripts.migrate_chat_tables

# Start backend
uvicorn src.main:app --reload --port 8000
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Verification Steps

1. **Health check**: `curl http://localhost:8000/health`
2. **Sign in**: Use existing auth flow to get JWT token
3. **Send chat message**:
   ```bash
   curl -X POST http://localhost:8000/api/{user_id}/chat \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{"message": "Show me my tasks"}'
   ```
4. **Verify response**: Should contain `conversation_id`, `response`, and `tool_calls`
5. **Check conversation history**: `GET /api/{user_id}/conversations`
6. **Open chat UI**: Navigate to `http://localhost:3000/dashboard/chat`

## Environment Variables (New)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | — | OpenAI API key for agent |
| `OPENAI_MODEL` | No | `gpt-4o` | OpenAI model for agent |

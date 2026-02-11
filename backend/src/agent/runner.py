"""Stateless agent runner.

Each call to run_chat:
1. Loads or creates conversation
2. Stores user message in DB
3. Reconstructs message history from DB
4. Builds function tools with user_id/session baked in
5. Runs the agent via Runner.run()
6. Extracts response and tool calls
7. Stores assistant message in DB
8. Returns ChatResponse
"""

import json
import logging
from uuid import UUID
from datetime import datetime

from agents import Agent, Runner, function_tool
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.conversation import Conversation
from models.message import Message
from schemas.chat import ChatResponse, ToolCallInfo
from agent.agent import SYSTEM_PROMPT
from agent import tools as tool_funcs
from config import settings

logger = logging.getLogger(__name__)

MAX_HISTORY_MESSAGES = 50


async def run_chat(
    user_id: UUID,
    message: str,
    conversation_id: UUID | None,
    session: AsyncSession,
) -> ChatResponse:
    """Execute one stateless chat turn."""

    # --- 1. Load or create conversation ---
    if conversation_id:
        result = await session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conversation not found or access denied",
            )
    else:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.flush()
        await session.refresh(conversation)

    # --- 2. Store user message ---
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=message,
    )
    session.add(user_msg)
    await session.flush()

    # --- 3. Reconstruct message history ---
    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    )
    all_messages = result.scalars().all()

    # Truncate if needed (keep last N messages)
    if len(all_messages) > MAX_HISTORY_MESSAGES:
        all_messages = all_messages[-MAX_HISTORY_MESSAGES:]

    # Build OpenAI-format messages
    openai_messages = []
    for msg in all_messages:
        openai_messages.append({
            "role": msg.role,
            "content": msg.content,
        })

    # --- 4. Build function tools with user_id/session baked in ---
    @function_tool
    async def create_task(title: str, description: str | None = None) -> str:
        """Create a new task with the given title and optional description."""
        result = await tool_funcs.create_task(session, user_id, title, description)
        return json.dumps(result)

    @function_tool
    async def list_tasks() -> str:
        """List all tasks for the current user."""
        result = await tool_funcs.list_tasks(session, user_id)
        return json.dumps(result)

    @function_tool
    async def get_task(task_id: str) -> str:
        """Get details of a specific task by its ID."""
        result = await tool_funcs.get_task(session, user_id, task_id)
        return json.dumps(result)

    @function_tool
    async def update_task(task_id: str, title: str | None = None, description: str | None = None) -> str:
        """Update a task's title and/or description."""
        result = await tool_funcs.update_task(session, user_id, task_id, title, description)
        return json.dumps(result)

    @function_tool
    async def delete_task(task_id: str) -> str:
        """Delete a task permanently by its ID."""
        result = await tool_funcs.delete_task(session, user_id, task_id)
        return json.dumps(result)

    @function_tool
    async def toggle_task(task_id: str) -> str:
        """Toggle a task's completion status (done/not done)."""
        result = await tool_funcs.toggle_task(session, user_id, task_id)
        return json.dumps(result)

    # --- 5. Create agent with tools and run ---
    agent = Agent(
        name="TodoAssistant",
        instructions=SYSTEM_PROMPT,
        model=settings.OPENAI_MODEL,
        tools=[create_task, list_tasks, get_task, update_task, delete_task, toggle_task],
    )

    import os
    os.environ.setdefault("OPENAI_API_KEY", settings.OPENAI_API_KEY)

    run_result = await Runner.run(
        agent,
        input=openai_messages,
    )

    # --- 6. Extract response and tool calls ---
    response_text = run_result.final_output or ""

    tool_call_infos: list[ToolCallInfo] = []
    # Parse tool usage from run_result if available
    for item in run_result.new_items:
        if hasattr(item, 'raw_item') and hasattr(item.raw_item, 'type'):
            if item.raw_item.type == "function_call_output":
                try:
                    result_data = json.loads(item.raw_item.output) if isinstance(item.raw_item.output, str) else item.raw_item.output
                except (json.JSONDecodeError, TypeError):
                    result_data = {"raw": str(item.raw_item.output)}

                tool_call_infos.append(ToolCallInfo(
                    tool_name=getattr(item.raw_item, 'name', 'unknown'),
                    parameters={},
                    result=result_data if isinstance(result_data, dict) else {"raw": str(result_data)},
                    success="error" not in (result_data if isinstance(result_data, dict) else {}),
                ))

    # --- 7. Store assistant message ---
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        tool_calls=[tc.model_dump() for tc in tool_call_infos] if tool_call_infos else None,
    )
    session.add(assistant_msg)

    # Update conversation metadata
    conversation.updated_at = datetime.utcnow()
    if not conversation.title:
        conversation.title = message[:100]
    session.add(conversation)

    await session.flush()

    # --- 8. Return response ---
    return ChatResponse(
        conversation_id=conversation.id,
        response=response_text,
        tool_calls=tool_call_infos,
    )

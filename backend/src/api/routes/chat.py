"""Chat API endpoints for AI agent interaction."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import get_session
from models.user import User
from models.conversation import Conversation
from models.message import Message
from schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationListResponse,
    ConversationSummary,
    MessageListResponse,
    MessageOut,
    ToolCallInfo,
)
from api.deps import get_current_user, verify_user_access

logger = logging.getLogger(__name__)
router = APIRouter()


# POST /api/{user_id}/chat
@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message to the AI agent",
)
async def send_chat_message(
    user_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    verify_user_access(user_id, current_user)

    logger.info(f"Chat message from user {current_user.id}: {request.message[:50]}...")

    try:
        from agent.runner import run_chat

        result = await run_chat(
            user_id=current_user.id,
            message=request.message,
            conversation_id=request.conversation_id,
            session=session,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent error for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI agent is temporarily unavailable. Please try again.",
        )


# GET /api/{user_id}/conversations
@router.get(
    "/{user_id}/conversations",
    response_model=ConversationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List user conversations",
)
async def list_conversations(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ConversationListResponse:
    verify_user_access(user_id, current_user)

    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()

    summaries = []
    for conv in conversations:
        # Get last message preview
        msg_result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_msg = msg_result.scalar_one_or_none()
        last_message = last_msg.content[:100] if last_msg else None

        summaries.append(
            ConversationSummary(
                id=conv.id,
                title=conv.title,
                last_message=last_message,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
            )
        )

    return ConversationListResponse(conversations=summaries)


# GET /api/{user_id}/conversations/{conversation_id}/messages
@router.get(
    "/{user_id}/conversations/{conversation_id}/messages",
    response_model=MessageListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get messages for a conversation",
)
async def get_conversation_messages(
    user_id: UUID,
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> MessageListResponse:
    verify_user_access(user_id, current_user)

    # Verify conversation ownership
    conv_result = await session.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = conv_result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Get all messages
    msg_result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = msg_result.scalars().all()

    message_list = []
    for msg in messages:
        tool_calls = None
        if msg.tool_calls:
            try:
                tool_calls = [ToolCallInfo(**tc) for tc in msg.tool_calls]
            except Exception:
                tool_calls = None

        message_list.append(
            MessageOut(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                tool_calls=tool_calls,
                created_at=msg.created_at,
            )
        )

    return MessageListResponse(
        conversation_id=conversation_id,
        messages=message_list,
    )

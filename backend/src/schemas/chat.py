from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional


class ChatRequest(BaseModel):
    """Request to send a chat message."""

    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[UUID] = None

    @field_validator('message')
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Message cannot be empty or whitespace only')
        return v.strip()


class ToolCallInfo(BaseModel):
    """Details of a single MCP tool invocation."""

    tool_name: str
    parameters: dict
    result: dict
    success: bool


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""

    conversation_id: UUID
    response: str
    tool_calls: list[ToolCallInfo] = []


class ConversationSummary(BaseModel):
    """Summary of a conversation for list view."""

    id: UUID
    title: Optional[str] = None
    last_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Response with list of conversations."""

    conversations: list[ConversationSummary]


class MessageOut(BaseModel):
    """Single message in a conversation."""

    id: UUID
    role: str
    content: str
    tool_calls: Optional[list[ToolCallInfo]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Response with messages for a conversation."""

    conversation_id: UUID
    messages: list[MessageOut]

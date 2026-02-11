from sqlmodel import SQLModel, Field, Column
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
import sqlalchemy as sa


class Message(SQLModel, table=True):
    """Single message within a conversation."""

    __tablename__ = "messages"
    __table_args__ = {"extend_existing": True}

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True,
    )

    role: str = Field(
        nullable=False,
    )

    content: str = Field(
        sa_column=Column(sa.Text, nullable=False),
    )

    tool_calls: Optional[dict] = Field(
        default=None,
        sa_column=Column(sa.JSON, nullable=True),
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )

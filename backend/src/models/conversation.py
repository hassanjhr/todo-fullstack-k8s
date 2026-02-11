from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class Conversation(SQLModel, table=True):
    """Chat conversation belonging to a user."""

    __tablename__ = "conversations"
    __table_args__ = {"extend_existing": True}

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
    )

    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
    )

    title: Optional[str] = Field(
        default=None,
        max_length=200,
        nullable=True,
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )

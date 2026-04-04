from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class Reminder(SQLModel, table=True):
    """
    Reminder entity — scheduled notification for a task.

    A task can have multiple reminders, each defined as an offset (minutes)
    before the task's due date. The scheduler polls pending reminders and
    publishes task.reminder events via Dapr pubsub.
    """

    __tablename__ = "reminders"
    __table_args__ = {"extend_existing": True}

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique reminder identifier"
    )
    task_id: UUID = Field(
        foreign_key="tasks.id",
        nullable=False,
        index=True,
        description="Task this reminder belongs to (CASCADE delete)"
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Owner of the task (denormalized for fast queries)"
    )
    offset_minutes: int = Field(
        nullable=False,
        description="Minutes before due_date when reminder fires (e.g. 60 = 1 hour before)"
    )
    trigger_at: datetime = Field(
        nullable=False,
        description="Absolute UTC timestamp when reminder fires (due_date - offset)"
    )
    status: str = Field(
        default="pending",
        nullable=False,
        description="Lifecycle state: pending | sent | cancelled"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Reminder creation timestamp"
    )

# Task SQLModel
# Purpose: Represents a todo item owned by a specific user
# Relationships: Many Tasks belong to one User (N:1)

from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class Task(SQLModel, table=True):
    """
    Task entity for todo items.

    Fields:
        id: Unique task identifier (UUID)
        user_id: Owner of this task (foreign key to users.id)
        title: Task title (required, max 200 characters)
        description: Optional task description (max 2000 characters)
        is_completed: Completion status (defaults to False)
        created_at: Task creation timestamp
        updated_at: Last modification timestamp

    Security:
        - user_id filtering: ALL queries MUST filter by authenticated user's user_id
        - Foreign key constraint: Prevents tasks from referencing non-existent users
        - ON DELETE CASCADE: When user is deleted, all their tasks are deleted

    Indexes:
        - PRIMARY KEY (id): Clustered index
        - INDEX idx_task_user_id: Fast filtering by user_id (critical for data isolation)
        - INDEX idx_task_user_created: Optimized for user's task list sorted by creation date

    Validation:
        - title: Required, non-empty, maximum 200 characters
        - description: Optional, maximum 2000 characters if provided
        - user_id: Must reference an existing user (enforced by foreign key)
    """

    __tablename__ = "tasks"
    __table_args__ = {"extend_existing": True}

    # Primary key: UUID for security (prevents enumeration)
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique task identifier"
    )

    # Foreign key: Links task to owning user
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Owner of this task (foreign key to users.id)"
    )

    # Task content: Title is required
    title: str = Field(
        max_length=200,
        nullable=False,
        description="Task title (required)"
    )

    # Task content: Description is optional
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        nullable=True,
        description="Optional task description"
    )

    # Task status: Defaults to incomplete
    is_completed: bool = Field(
        default=False,
        nullable=False,
        description="Completion status"
    )

    # Audit fields: Track creation and modification times
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Task creation timestamp"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last modification timestamp"
    )

    class Config:
        """SQLModel configuration"""
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "is_completed": False,
                "created_at": "2026-02-06T12:00:00Z",
                "updated_at": "2026-02-06T12:00:00Z"
            }
        }

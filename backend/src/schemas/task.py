# Task Pydantic Schemas (T030)
# Purpose: Request and response models for task management
# Security: Task ownership enforced via JWT authentication

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional


# ============================================================================
# Request Schemas (Input Validation)
# ============================================================================

class TaskCreateRequest(BaseModel):
    """
    Request schema for creating a new task.

    Fields:
        title: Task title (required, max 200 characters)
        description: Optional task description (max 2000 characters)

    Validation:
        - Title is required and cannot be empty or whitespace only
        - Title maximum length: 200 characters
        - Description is optional
        - Description maximum length: 2000 characters if provided

    Security:
        - user_id is NOT in request body (determined from JWT token)
        - Task ownership assigned from authenticated user
        - is_completed defaults to False (not user-controllable on creation)

    Example:
        {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread"
        }
    """
    title: str = Field(
        ...,
        max_length=200,
        description="Task title (required, max 200 characters)",
        examples=["Buy groceries"]
    )

    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional task description (max 2000 characters)",
        examples=["Milk, eggs, bread"]
    )

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """
        Validate title is not empty or whitespace only.

        Security: Prevents creation of tasks with meaningless titles.
        """
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_strip(cls, v: Optional[str]) -> Optional[str]:
        """
        Strip whitespace from description if provided.

        Returns None if description is empty or whitespace only.
        """
        if v is None:
            return None
        stripped = v.strip()
        return stripped if stripped else None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        }


class TaskUpdateRequest(BaseModel):
    """
    Request schema for updating an existing task.

    Fields:
        title: Task title (required, max 200 characters)
        description: Optional task description (max 2000 characters)

    Validation:
        - Title is required and cannot be empty or whitespace only
        - Title maximum length: 200 characters
        - Description is optional
        - Description maximum length: 2000 characters if provided

    Security:
        - Task ownership verified via JWT token before update
        - Only task owner can update their tasks
        - is_completed NOT updatable via this endpoint (use PATCH /complete)

    Example:
        {
            "title": "Buy groceries and household items",
            "description": "Milk, eggs, bread, cleaning supplies"
        }
    """
    title: str = Field(
        ...,
        max_length=200,
        description="Task title (required, max 200 characters)",
        examples=["Buy groceries and household items"]
    )

    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional task description (max 2000 characters)",
        examples=["Milk, eggs, bread, cleaning supplies"]
    )

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """
        Validate title is not empty or whitespace only.

        Security: Prevents updating tasks with meaningless titles.
        """
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_strip(cls, v: Optional[str]) -> Optional[str]:
        """
        Strip whitespace from description if provided.

        Returns None if description is empty or whitespace only.
        """
        if v is None:
            return None
        stripped = v.strip()
        return stripped if stripped else None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries and household items",
                "description": "Milk, eggs, bread, cleaning supplies"
            }
        }


# ============================================================================
# Response Schemas (Output Serialization)
# ============================================================================

class TaskResponse(BaseModel):
    """
    Response schema for a single task.

    Fields:
        id: Task unique identifier (UUID)
        user_id: Owner of this task (UUID)
        title: Task title
        description: Optional task description
        is_completed: Completion status
        created_at: Task creation timestamp
        updated_at: Last modification timestamp

    Security:
        - user_id exposed to verify ownership
        - Only returns tasks belonging to authenticated user
        - Safe to return in API responses

    Example:
        {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "is_completed": false,
            "created_at": "2026-02-06T12:00:00Z",
            "updated_at": "2026-02-06T12:00:00Z"
        }
    """
    id: UUID = Field(
        ...,
        description="Task unique identifier",
        examples=["660e8400-e29b-41d4-a716-446655440001"]
    )

    user_id: UUID = Field(
        ...,
        description="Owner of this task",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    title: str = Field(
        ...,
        description="Task title",
        examples=["Buy groceries"]
    )

    description: Optional[str] = Field(
        default=None,
        description="Optional task description",
        examples=["Milk, eggs, bread"]
    )

    is_completed: bool = Field(
        ...,
        description="Completion status",
        examples=[False]
    )

    created_at: datetime = Field(
        ...,
        description="Task creation timestamp (UTC)",
        examples=["2026-02-06T12:00:00Z"]
    )

    updated_at: datetime = Field(
        ...,
        description="Last modification timestamp (UTC)",
        examples=["2026-02-06T12:00:00Z"]
    )

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel compatibility
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "is_completed": False,
                "created_at": "2026-02-06T12:00:00.000Z",
                "updated_at": "2026-02-06T12:00:00.000Z"
            }
        }


class TaskListResponse(BaseModel):
    """
    Response schema for list of tasks.

    Fields:
        tasks: List of TaskResponse objects

    Security:
        - Only contains tasks belonging to authenticated user
        - Filtered by user_id from JWT token

    Example:
        {
            "tasks": [
                {
                    "id": "660e8400-e29b-41d4-a716-446655440001",
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                    "is_completed": false,
                    "created_at": "2026-02-06T12:00:00Z",
                    "updated_at": "2026-02-06T12:00:00Z"
                }
            ]
        }
    """
    tasks: list[TaskResponse] = Field(
        ...,
        description="List of tasks belonging to authenticated user"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "id": "660e8400-e29b-41d4-a716-446655440001",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "is_completed": False,
                        "created_at": "2026-02-06T12:00:00.000Z",
                        "updated_at": "2026-02-06T12:00:00.000Z"
                    },
                    {
                        "id": "660e8400-e29b-41d4-a716-446655440002",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Finish project",
                        "description": None,
                        "is_completed": False,
                        "created_at": "2026-02-06T13:00:00.000Z",
                        "updated_at": "2026-02-06T13:00:00.000Z"
                    }
                ]
            }
        }

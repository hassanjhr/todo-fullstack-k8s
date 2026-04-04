# Task Pydantic Schemas (Extended: 005-advanced-features-dapr-kafka)
# Purpose: Request and response models for task management with priorities, tags,
#          due dates, recurrence, and reminders.
# Security: Task ownership enforced via JWT authentication

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional, List


# ============================================================================
# Reminder sub-schema (used inside TaskResponse)
# ============================================================================

class ReminderInTask(BaseModel):
    id: UUID
    offset_minutes: int
    trigger_at: datetime
    status: str

    class Config:
        from_attributes = True


# ============================================================================
# Request Schemas (Input Validation)
# ============================================================================

class TaskCreateRequest(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    # Advanced fields
    priority: str = Field(default="medium")
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[datetime] = Field(default=None)
    recurrence_rule: Optional[str] = Field(default=None)
    reminders: List[int] = Field(default_factory=list, description="List of offset_minutes for reminders")

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_strip(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        stripped = v.strip()
        return stripped if stripped else None

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        if v not in ('high', 'medium', 'low'):
            raise ValueError("priority must be one of: high, medium, low")
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        import re
        result = []
        for tag in v:
            tag = tag.strip().lower()
            if tag and re.match(r'^[a-zA-Z0-9\-]+$', tag):
                if len(tag) <= 50:
                    result.append(tag)
        return list(dict.fromkeys(result))  # deduplicate preserving order

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "priority": "high",
                "tags": ["work", "urgent"],
                "due_date": "2026-04-02T09:00:00Z",
                "recurrence_rule": None,
                "reminders": [60]
            }
        }


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    is_completed: Optional[bool] = Field(default=None)
    # Advanced fields
    priority: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    due_date: Optional[datetime] = Field(default=None)
    recurrence_rule: Optional[str] = Field(default=None)
    is_paused: Optional[bool] = Field(default=None)
    update_scope: str = Field(default="this_only")

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ('high', 'medium', 'low'):
            raise ValueError("priority must be one of: high, medium, low")
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return None
        import re
        result = []
        for tag in v:
            tag = tag.strip().lower()
            if tag and re.match(r'^[a-zA-Z0-9\-]+$', tag):
                if len(tag) <= 50:
                    result.append(tag)
        return list(dict.fromkeys(result))


# ============================================================================
# Response Schemas (Output Serialization)
# ============================================================================

class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str] = None
    is_completed: bool
    # Advanced fields
    priority: str = "medium"
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[datetime] = None
    is_overdue: bool = False
    recurrence_rule: Optional[str] = None
    series_id: Optional[UUID] = None
    is_paused: bool = False
    next_due_date: Optional[datetime] = None
    reminders: List[ReminderInTask] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    next_cursor: Optional[str] = None
    has_more: bool = False

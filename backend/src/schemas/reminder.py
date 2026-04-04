"""
Reminder Pydantic Schemas
Feature: 005-advanced-features-dapr-kafka
"""

from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime


class ReminderCreateRequest(BaseModel):
    offset_minutes: int

    @field_validator('offset_minutes')
    @classmethod
    def validate_offset(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('offset_minutes must be greater than 0')
        return v


class ReminderResponse(BaseModel):
    id: UUID
    offset_minutes: int
    trigger_at: datetime
    status: str

    class Config:
        from_attributes = True

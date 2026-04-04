"""
Tag Pydantic Schemas
Feature: 005-advanced-features-dapr-kafka
"""

import re
from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID


class TagCreateRequest(BaseModel):
    name: str
    color: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError('Tag name cannot be empty')
        if len(v) > 50:
            raise ValueError('Tag name must be 50 characters or fewer')
        if not re.match(r'^[a-zA-Z0-9\-]+$', v):
            raise ValueError('Tag name must contain only letters, numbers, and hyphens')
        return v

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex code e.g. #FF5733')
        return v


class TagResponse(BaseModel):
    id: UUID
    name: str
    color: Optional[str] = None
    task_count: int = 0

    class Config:
        from_attributes = True


class TagListResponse(BaseModel):
    tags: list[TagResponse]

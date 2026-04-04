# Tags API Routes
# Feature: 005-advanced-features-dapr-kafka
# Purpose: CRUD endpoints for user-scoped tags
# Security: JWT authentication required, all operations scoped to authenticated user

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy import func
from uuid import UUID
from datetime import datetime
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import get_session
from models.user import User
from models.tag import Tag
from models.task_tag import TaskTag
from schemas.tag import TagCreateRequest, TagResponse, TagListResponse
from api.deps import get_current_user, verify_user_access

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# GET /api/{user_id}/tags — List user's tags with task counts
# ============================================================================

@router.get(
    "/{user_id}/tags",
    response_model=TagListResponse,
    status_code=status.HTTP_200_OK,
    summary="List user's tags",
)
async def get_tags(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TagListResponse:
    verify_user_access(user_id, current_user)

    # Fetch all tags for the user
    stmt = (
        select(Tag)
        .where(Tag.user_id == current_user.id)
        .order_by(Tag.name)
    )
    result = await session.execute(stmt)
    tags = list(result.scalars().all())

    if not tags:
        return TagListResponse(tags=[])

    # Batch-fetch task counts to avoid N+1
    tag_ids = [t.id for t in tags]
    count_stmt = (
        select(TaskTag.tag_id, func.count(TaskTag.task_id).label("cnt"))
        .where(TaskTag.tag_id.in_(tag_ids))
        .group_by(TaskTag.tag_id)
    )
    count_result = await session.execute(count_stmt)
    counts: dict[UUID, int] = {row.tag_id: row.cnt for row in count_result.all()}

    tag_responses = [
        TagResponse(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            task_count=counts.get(tag.id, 0),
        )
        for tag in tags
    ]

    logger.info(f"Retrieved {len(tag_responses)} tags for user {current_user.id}")
    return TagListResponse(tags=tag_responses)


# ============================================================================
# POST /api/{user_id}/tags — Create a new tag
# ============================================================================

@router.post(
    "/{user_id}/tags",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a tag",
    responses={
        409: {"description": "Tag with this name already exists"},
    },
)
async def create_tag(
    user_id: UUID,
    tag_data: TagCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TagResponse:
    verify_user_access(user_id, current_user)

    # Check for duplicate (UNIQUE(user_id, name) enforced at DB level too)
    dup_stmt = select(Tag).where(
        Tag.user_id == current_user.id,
        Tag.name == tag_data.name,
    )
    dup_result = await session.execute(dup_stmt)
    if dup_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tag '{tag_data.name}' already exists",
        )

    new_tag = Tag(
        user_id=current_user.id,
        name=tag_data.name,
        color=tag_data.color,
        created_at=datetime.utcnow(),
    )
    session.add(new_tag)
    await session.commit()
    await session.refresh(new_tag)

    logger.info(f"Tag '{new_tag.name}' created for user {current_user.id}")
    return TagResponse(id=new_tag.id, name=new_tag.name, color=new_tag.color, task_count=0)


# ============================================================================
# DELETE /api/{user_id}/tags/{tag_id} — Delete a tag (cascades to task_tags)
# ============================================================================

@router.delete(
    "/{user_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a tag",
    responses={
        404: {"description": "Tag not found"},
    },
)
async def delete_tag(
    user_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    verify_user_access(user_id, current_user)

    stmt = select(Tag).where(
        Tag.id == tag_id,
        Tag.user_id == current_user.id,
    )
    result = await session.execute(stmt)
    tag = result.scalar_one_or_none()

    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    await session.delete(tag)
    await session.commit()

    logger.info(f"Tag {tag_id} deleted for user {current_user.id}")
    return None

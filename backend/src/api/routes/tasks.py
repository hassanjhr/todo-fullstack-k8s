# Task API Routes (T031, T032)
# Purpose: CRUD endpoints for task management
# Security: JWT authentication required, user data isolation enforced

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from uuid import UUID
from datetime import datetime
import logging

# Import dependencies
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import get_session
from models.user import User
from models.task import Task
from schemas.task import TaskCreateRequest, TaskUpdateRequest, TaskResponse, TaskListResponse
from api.deps import get_current_user, verify_user_access

# Configure logging
logger = logging.getLogger(__name__)

# Create router for task endpoints
router = APIRouter()


# ============================================================================
# GET /api/{user_id}/tasks - Retrieve User's Tasks (T031)
# ============================================================================

@router.get(
    "/{user_id}/tasks",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's tasks",
    description="Retrieve all tasks belonging to the authenticated user, sorted by creation date (newest first)",
    responses={
        200: {
            "description": "Tasks retrieved successfully",
            "content": {
                "application/json": {
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
                            }
                        ]
                    }
                }
            }
        },
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        403: {"description": "Forbidden - user_id does not match authenticated user"}
    }
)
async def get_tasks(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> TaskListResponse:
    """
    Retrieve all tasks belonging to the authenticated user.

    Security Flow:
        1. Extract and verify JWT token (via get_current_user dependency)
        2. Verify user_id in URL matches authenticated user's ID
        3. Query tasks filtered by authenticated user_id
        4. Return tasks sorted by created_at DESC (newest first)

    Args:
        user_id: User ID from URL path parameter
        current_user: Authenticated user from JWT token
        session: Database session for queries

    Returns:
        TaskListResponse: List of tasks belonging to authenticated user

    Raises:
        HTTPException 401: If JWT token is invalid or missing
        HTTPException 403: If user_id does not match authenticated user

    Security:
        - ALL tasks filtered by authenticated user_id from JWT token
        - user_id in URL must match authenticated user (prevents cross-user access)
        - No pagination limit (acceptable for MVP; add pagination in production)

    Example Request:
        GET /api/550e8400-e29b-41d4-a716-446655440000/tasks
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    Example Response (200 OK):
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
    # Verify user_id in URL matches authenticated user (403 if mismatch)
    verify_user_access(user_id, current_user)

    logger.info(f"Retrieving tasks for user {current_user.id}")

    # Query tasks filtered by authenticated user_id
    # Security: CRITICAL - Filter by current_user.id from JWT token, NOT user_id from URL
    statement = (
        select(Task)
        .where(Task.user_id == current_user.id)
        .order_by(Task.created_at.desc())  # Newest first
    )

    result = await session.execute(statement)
    tasks = result.scalars().all()

    logger.info(f"Retrieved {len(tasks)} tasks for user {current_user.id}")

    # Convert SQLModel objects to Pydantic response models
    task_responses = [TaskResponse.model_validate(task) for task in tasks]

    return TaskListResponse(tasks=task_responses)


# ============================================================================
# GET /api/{user_id}/tasks/{task_id} - Get Single Task (T049)
# ============================================================================

@router.get(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single task",
    description="Retrieve full details of a single task (authenticated user must own the task)",
    responses={
        200: {
            "description": "Task retrieved successfully",
            "content": {
                "application/json": {
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
            }
        },
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        403: {"description": "Forbidden - user_id does not match authenticated user"},
        404: {"description": "Not Found - Task does not exist or does not belong to user"}
    }
)
async def get_single_task(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> TaskResponse:
    """
    Retrieve full details of a single task.

    Security Flow:
        1. Extract and verify JWT token (via get_current_user dependency)
        2. Verify user_id in URL matches authenticated user's ID
        3. Query task by task_id with ownership filter (Task.user_id == current_user.id)
        4. Return 404 if task not found (prevents task enumeration attacks)
        5. Return complete task object with all fields

    Args:
        user_id: User ID from URL path parameter
        task_id: Task ID from URL path parameter
        current_user: Authenticated user from JWT token
        session: Database session for queries

    Returns:
        TaskResponse: Complete task object with all fields

    Raises:
        HTTPException 401: If JWT token is invalid or missing
        HTTPException 403: If user_id does not match authenticated user
        HTTPException 404: If task not found or does not belong to authenticated user

    Security:
        - Task ownership verified via JWT token AND database query
        - user_id in URL must match authenticated user (prevents cross-user access)
        - Task query filtered by current_user.id (prevents viewing other users' tasks)
        - Returns 404 for non-existent tasks (prevents enumeration of task IDs)

    Example Request:
        GET /api/550e8400-e29b-41d4-a716-446655440000/tasks/660e8400-e29b-41d4-a716-446655440001
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    Example Response (200 OK):
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
    # Verify user_id in URL matches authenticated user (403 if mismatch)
    verify_user_access(user_id, current_user)

    logger.info(f"Retrieving task {task_id} for user {current_user.id}")

    # Query task with ownership verification
    # Security: CRITICAL - Filter by both task_id AND current_user.id to ensure ownership
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id  # Ownership check
    )

    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    # Return 404 if task not found (don't reveal if task exists for other users)
    if not task:
        logger.warning(f"Task {task_id} not found or does not belong to user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    logger.info(f"Task {task_id} retrieved successfully for user {current_user.id}")

    # Convert SQLModel object to Pydantic response model
    return TaskResponse.model_validate(task)


# ============================================================================
# POST /api/{user_id}/tasks - Create New Task (T032)
# ============================================================================

@router.post(
    "/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new task",
    description="Create a new task for the authenticated user",
    responses={
        201: {
            "description": "Task created successfully",
            "content": {
                "application/json": {
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
            }
        },
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        403: {"description": "Forbidden - user_id does not match authenticated user"},
        422: {"description": "Validation error - Invalid request body"}
    }
)
async def create_task(
    user_id: UUID,
    task_data: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> TaskResponse:
    """
    Create a new task for the authenticated user.

    Security Flow:
        1. Extract and verify JWT token (via get_current_user dependency)
        2. Verify user_id in URL matches authenticated user's ID
        3. Validate request body (title required, max lengths enforced)
        4. Create task with authenticated user_id from JWT token
        5. Set is_completed to False by default
        6. Save to database and return created task

    Args:
        user_id: User ID from URL path parameter
        task_data: Task creation request (title, optional description)
        current_user: Authenticated user from JWT token
        session: Database session for queries

    Returns:
        TaskResponse: Created task with generated ID and timestamps

    Raises:
        HTTPException 401: If JWT token is invalid or missing
        HTTPException 403: If user_id does not match authenticated user
        HTTPException 422: If validation fails (empty title, too long, etc.)

    Security:
        - Task ownership determined by JWT token, NOT request body
        - user_id assigned from current_user.id (authenticated user)
        - user_id in URL must match authenticated user (prevents creating tasks for others)
        - is_completed defaults to False (not user-controllable on creation)

    Validation:
        - title: Required, non-empty, max 200 characters
        - description: Optional, max 2000 characters if provided

    Example Request:
        POST /api/550e8400-e29b-41d4-a716-446655440000/tasks
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        Content-Type: application/json

        {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread"
        }

    Example Response (201 Created):
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
    # Verify user_id in URL matches authenticated user (403 if mismatch)
    verify_user_access(user_id, current_user)

    logger.info(f"Creating task for user {current_user.id}: {task_data.title}")

    # Create task with authenticated user_id from JWT token
    # Security: CRITICAL - Use current_user.id from JWT, NOT user_id from URL or request body
    now = datetime.utcnow()
    new_task = Task(
        user_id=current_user.id,  # From JWT token, not request
        title=task_data.title,
        description=task_data.description,
        is_completed=False,  # Default to incomplete
        created_at=now,
        updated_at=now
    )

    # Save to database
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    logger.info(f"Task created successfully: {new_task.id} for user {current_user.id}")

    # Convert SQLModel object to Pydantic response model
    return TaskResponse.model_validate(new_task)


# ============================================================================
# PUT /api/{user_id}/tasks/{task_id} - Update Task (T040)
# ============================================================================

@router.put(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update task",
    description="Update an existing task's title and description (authenticated user must own the task)",
    responses={
        200: {
            "description": "Task updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "660e8400-e29b-41d4-a716-446655440001",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Buy groceries and household items",
                        "description": "Milk, eggs, bread, cleaning supplies",
                        "is_completed": False,
                        "created_at": "2026-02-06T12:00:00.000Z",
                        "updated_at": "2026-02-07T10:30:00.000Z"
                    }
                }
            }
        },
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        403: {"description": "Forbidden - user_id does not match authenticated user"},
        404: {"description": "Not Found - Task does not exist or does not belong to user"},
        422: {"description": "Validation error - Invalid request body"}
    }
)
async def update_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> TaskResponse:
    """
    Update an existing task's title and description.

    Security Flow:
        1. Extract and verify JWT token (via get_current_user dependency)
        2. Verify user_id in URL matches authenticated user's ID
        3. Query task by task_id with ownership filter (Task.user_id == current_user.id)
        4. Return 404 if task not found (prevents task enumeration attacks)
        5. Validate request body (title required, max lengths enforced)
        6. Update title and description fields
        7. Update updated_at timestamp automatically
        8. Save to database and return updated task

    Args:
        user_id: User ID from URL path parameter
        task_id: Task ID from URL path parameter
        task_data: Task update request (title, optional description)
        current_user: Authenticated user from JWT token
        session: Database session for queries

    Returns:
        TaskResponse: Updated task with new values and updated timestamp

    Raises:
        HTTPException 401: If JWT token is invalid or missing
        HTTPException 403: If user_id does not match authenticated user
        HTTPException 404: If task not found or does not belong to authenticated user
        HTTPException 422: If validation fails (empty title, too long, etc.)

    Security:
        - Task ownership verified via JWT token AND database query
        - user_id in URL must match authenticated user (prevents cross-user access)
        - Task query filtered by current_user.id (prevents updating other users' tasks)
        - Returns 404 for non-existent tasks (prevents enumeration of task IDs)
        - is_completed NOT updatable via this endpoint (use PATCH /complete)

    Validation:
        - title: Required, non-empty, max 200 characters
        - description: Optional, max 2000 characters if provided

    Example Request:
        PUT /api/550e8400-e29b-41d4-a716-446655440000/tasks/660e8400-e29b-41d4-a716-446655440001
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        Content-Type: application/json

        {
            "title": "Buy groceries and household items",
            "description": "Milk, eggs, bread, cleaning supplies"
        }

    Example Response (200 OK):
        {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Buy groceries and household items",
            "description": "Milk, eggs, bread, cleaning supplies",
            "is_completed": false,
            "created_at": "2026-02-06T12:00:00Z",
            "updated_at": "2026-02-07T10:30:00Z"
        }
    """
    # Verify user_id in URL matches authenticated user (403 if mismatch)
    verify_user_access(user_id, current_user)

    logger.info(f"Updating task {task_id} for user {current_user.id}")

    # Query task with ownership verification
    # Security: CRITICAL - Filter by both task_id AND current_user.id to ensure ownership
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id  # Ownership check
    )

    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    # Return 404 if task not found (don't reveal if task exists for other users)
    if not task:
        logger.warning(f"Task {task_id} not found or does not belong to user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update task fields
    task.title = task_data.title
    task.description = task_data.description
    task.updated_at = datetime.utcnow()  # Update timestamp

    # Save changes to database
    session.add(task)
    await session.commit()
    await session.refresh(task)

    logger.info(f"Task {task_id} updated successfully for user {current_user.id}")

    # Convert SQLModel object to Pydantic response model
    return TaskResponse.model_validate(task)


# ============================================================================
# DELETE /api/{user_id}/tasks/{task_id} - Delete Task (T041)
# ============================================================================

@router.delete(
    "/{user_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Permanently delete a task (authenticated user must own the task)",
    responses={
        204: {"description": "Task deleted successfully (no response body)"},
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        403: {"description": "Forbidden - user_id does not match authenticated user"},
        404: {"description": "Not Found - Task does not exist or does not belong to user"}
    }
)
async def delete_task(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Permanently delete a task.

    Security Flow:
        1. Extract and verify JWT token (via get_current_user dependency)
        2. Verify user_id in URL matches authenticated user's ID
        3. Query task by task_id with ownership filter (Task.user_id == current_user.id)
        4. Return 404 if task not found (prevents task enumeration attacks)
        5. Delete task from database (permanent deletion)
        6. Return 204 No Content status (no response body)

    Args:
        user_id: User ID from URL path parameter
        task_id: Task ID from URL path parameter
        current_user: Authenticated user from JWT token
        session: Database session for queries

    Returns:
        None: 204 No Content status with no response body

    Raises:
        HTTPException 401: If JWT token is invalid or missing
        HTTPException 403: If user_id does not match authenticated user
        HTTPException 404: If task not found or does not belong to authenticated user

    Security:
        - Task ownership verified via JWT token AND database query
        - user_id in URL must match authenticated user (prevents cross-user access)
        - Task query filtered by current_user.id (prevents deleting other users' tasks)
        - Returns 404 for non-existent tasks (prevents enumeration of task IDs)
        - Deletion is permanent (no soft delete in MVP)

    Example Request:
        DELETE /api/550e8400-e29b-41d4-a716-446655440000/tasks/660e8400-e29b-41d4-a716-446655440001
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    Example Response (204 No Content):
        (No response body)
    """
    # Verify user_id in URL matches authenticated user (403 if mismatch)
    verify_user_access(user_id, current_user)

    logger.info(f"Deleting task {task_id} for user {current_user.id}")

    # Query task with ownership verification
    # Security: CRITICAL - Filter by both task_id AND current_user.id to ensure ownership
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id  # Ownership check
    )

    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    # Return 404 if task not found (don't reveal if task exists for other users)
    if not task:
        logger.warning(f"Task {task_id} not found or does not belong to user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Delete task from database (permanent deletion)
    await session.delete(task)
    await session.commit()

    logger.info(f"Task {task_id} deleted successfully for user {current_user.id}")

    # Return 204 No Content (no response body)
    return None


# ============================================================================
# PATCH /api/{user_id}/tasks/{task_id}/complete - Toggle Task Completion (T045)
# ============================================================================

@router.patch(
    "/{user_id}/tasks/{task_id}/complete",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle task completion",
    description="Toggle the completion status of a task (complete ↔ incomplete)",
    responses={
        200: {
            "description": "Task completion status toggled successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "660e8400-e29b-41d4-a716-446655440001",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "is_completed": True,
                        "created_at": "2026-02-06T12:00:00.000Z",
                        "updated_at": "2026-02-07T10:30:00.000Z"
                    }
                }
            }
        },
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        403: {"description": "Forbidden - user_id does not match authenticated user"},
        404: {"description": "Not Found - Task does not exist or does not belong to user"}
    }
)
async def toggle_task_completion(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> TaskResponse:
    """
    Toggle the completion status of a task (complete ↔ incomplete).

    Security Flow:
        1. Extract and verify JWT token (via get_current_user dependency)
        2. Verify user_id in URL matches authenticated user's ID
        3. Query task by task_id with ownership filter (Task.user_id == current_user.id)
        4. Return 404 if task not found (prevents task enumeration attacks)
        5. Toggle is_completed field (True → False, False → True)
        6. Update updated_at timestamp automatically
        7. Save to database and return updated task

    Args:
        user_id: User ID from URL path parameter
        task_id: Task ID from URL path parameter
        current_user: Authenticated user from JWT token
        session: Database session for queries

    Returns:
        TaskResponse: Updated task with toggled completion status

    Raises:
        HTTPException 401: If JWT token is invalid or missing
        HTTPException 403: If user_id does not match authenticated user
        HTTPException 404: If task not found or does not belong to authenticated user

    Security:
        - Task ownership verified via JWT token AND database query
        - user_id in URL must match authenticated user (prevents cross-user access)
        - Task query filtered by current_user.id (prevents toggling other users' tasks)
        - Returns 404 for non-existent tasks (prevents enumeration of task IDs)

    Toggle Logic:
        - If is_completed is True, set to False
        - If is_completed is False, set to True
        - Simple boolean negation: task.is_completed = not task.is_completed

    Example Request:
        PATCH /api/550e8400-e29b-41d4-a716-446655440000/tasks/660e8400-e29b-41d4-a716-446655440001/complete
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    Example Response (200 OK):
        {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "is_completed": true,
            "created_at": "2026-02-06T12:00:00Z",
            "updated_at": "2026-02-07T10:30:00Z"
        }
    """
    # Verify user_id in URL matches authenticated user (403 if mismatch)
    verify_user_access(user_id, current_user)

    logger.info(f"Toggling completion status for task {task_id} for user {current_user.id}")

    # Query task with ownership verification
    # Security: CRITICAL - Filter by both task_id AND current_user.id to ensure ownership
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id  # Ownership check
    )

    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    # Return 404 if task not found (don't reveal if task exists for other users)
    if not task:
        logger.warning(f"Task {task_id} not found or does not belong to user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Toggle completion status (True → False, False → True)
    task.is_completed = not task.is_completed
    task.updated_at = datetime.utcnow()  # Update timestamp

    # Save changes to database
    session.add(task)
    await session.commit()
    await session.refresh(task)

    logger.info(f"Task {task_id} completion toggled to {task.is_completed} for user {current_user.id}")

    # Convert SQLModel object to Pydantic response model
    return TaskResponse.model_validate(task)

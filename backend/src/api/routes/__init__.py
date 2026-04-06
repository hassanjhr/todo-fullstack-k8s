# API Routes
# Purpose: API endpoint routers for different resource types

from .auth import router as auth_router
from .tasks import router as tasks_router
from .chat import router as chat_router
from .tags import router as tags_router
from .reminders import router as reminders_router
from .dapr_bindings import router as dapr_bindings_router

__all__ = ["auth_router", "tasks_router", "chat_router", "tags_router", "reminders_router", "dapr_bindings_router"]

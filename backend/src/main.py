# FastAPI Application Entry Point
# Purpose: Main application configuration with CORS, database lifecycle, and health check
# Security: JWT authentication, CORS restrictions, proper error handling

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
from src.api.routes.auth import router as auth_router
from src.api.routes.tasks import router as tasks_router



# Import configuration and database
# from config import settings
from src.config import settings

# from database import init_db, close_db
from src.database import init_db, close_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# Application Lifecycle Management
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events for database connections.

    Startup:
        - Log application start
        - Initialize database connection pool
        - Log configuration (non-sensitive)

    Shutdown:
        - Close database connection pool
        - Log application shutdown
    """
    # Startup
    logger.info("Starting Todo Full-Stack Web Application")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Backend Host: {settings.BACKEND_HOST}:{settings.BACKEND_PORT}")
    logger.info(f"Frontend URL: {settings.FRONTEND_URL}")
    logger.info(f"JWT Algorithm: {settings.JWT_ALGORITHM}")
    logger.info(f"JWT Expiration: {settings.JWT_EXPIRATION_HOURS} hours")

    # Create tables for any new models (conversations, messages)
    await init_db()

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")
    await close_db()
    logger.info("Database connections closed")


# ============================================================================
# FastAPI Application Instance (T015)
# ============================================================================

app = FastAPI(
    title="Todo Full-Stack Web Application API",
    description="RESTful API for multi-user todo management with JWT authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# ============================================================================
# CORS Middleware Configuration (T014)
# ============================================================================

# Configure CORS to allow frontend origin
# Security: Only allow requests from configured frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Frontend origins from environment (comma-separated)
    allow_credentials=True,  # Allow cookies and Authorization headers
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],  # Allowed HTTP methods
    allow_headers=[
        "Authorization",  # JWT token in Bearer scheme
        "Content-Type",  # JSON request/response bodies
        "Accept",  # Content negotiation
        "Origin",  # CORS preflight
        "X-Requested-With",  # AJAX requests
    ],
    expose_headers=[
        "Content-Length",
        "Content-Type",
    ],
    max_age=3600,  # Cache preflight requests for 1 hour
)

logger.info(f"CORS configured for origin: {settings.FRONTEND_URL}")


# ============================================================================
# Global Exception Handlers
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors with detailed field-level messages.

    Returns 422 Unprocessable Entity with error details.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(f"Validation error on {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions with safe error messages.

    Returns 500 Internal Server Error without exposing sensitive details.
    """
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get(
    "/health",
    tags=["Health"],
    summary="Health check endpoint",
    description="Returns application health status and version information",
    response_description="Application is healthy and running"
)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Health status, version, and environment information

    Status Codes:
        200: Application is healthy

    Example Response:
        {
            "status": "healthy",
            "version": "1.0.0",
            "environment": "development"
        }
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get(
    "/",
    tags=["Root"],
    summary="API root endpoint",
    description="Returns API information and documentation links"
)
async def root():
    """
    Root endpoint with API information.

    Returns:
        dict: API name, version, and documentation links
    """
    return {
        "name": "Todo Full-Stack Web Application API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


# ============================================================================
# API Router Registration (T023, T033)
# ============================================================================

# Import authentication, task, and chat routes
from api.routes import auth_router, tasks_router, chat_router

# Register authentication routes
# Security: Auth endpoints do NOT require JWT authentication (they issue tokens)
app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"]
)

logger.info("Authentication routes registered at /api/auth")

# Register task routes (T033)
# Security: Task endpoints REQUIRE JWT authentication (protected by get_current_user dependency)
app.include_router(
    tasks_router,
    prefix="/api",
    tags=["Tasks"]
)

logger.info("Task routes registered at /api")

# Register chat routes
app.include_router(
    chat_router,
    prefix="/api",
    tags=["Chat"]
)

logger.info("Chat routes registered at /api")


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )

# Environment Configuration Loader
# Purpose: Load and validate environment variables for the application
# Security: All secrets must be loaded from environment, never hardcoded

import os
import logging
from pydantic_settings import BaseSettings
from typing import List, Optional

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    Required Variables:
        DATABASE_URL: PostgreSQL connection string
        JWT_SECRET_KEY: Secret key for JWT token signing (minimum 32 characters)
        FRONTEND_URL: Frontend origin for CORS configuration

    Optional Variables:
        JWT_ALGORITHM: JWT signing algorithm (default: HS256)
        JWT_EXPIRATION_HOURS: Token expiration time in hours (default: 24)
        BACKEND_HOST: Server host (default: 0.0.0.0)
        BACKEND_PORT: Server port (default: 8000)
        ENVIRONMENT: Deployment environment (default: development)

    Usage:
        from config import settings
        print(settings.DATABASE_URL)
    """

    # Database Configuration (Required)
    DATABASE_URL: str

    # JWT Configuration (Required)
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # CORS Configuration (Required)
    # Comma-separated list of allowed origins (e.g., "http://localhost:3000,https://myapp.vercel.app")
    FRONTEND_URL: str

    @property
    def cors_origins(self) -> List[str]:
        """Parse FRONTEND_URL into a list of origins (supports comma-separated values).
        In development mode, allows all origins to support Minikube random tunnel ports."""
        if self.ENVIRONMENT == "development":
            return ["*"]
        return [origin.strip() for origin in self.FRONTEND_URL.split(",") if origin.strip()]

    # Server Configuration (Optional)
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # OpenAI Agent Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # Environment (Optional)
    ENVIRONMENT: str = "development"

    # Dapr Configuration (005-advanced-features-dapr-kafka)
    DAPR_ENABLED: bool = False
    DAPR_HTTP_PORT: int = 3500
    DAPR_PUBSUB_NAME: str = "taskpubsub"
    REMINDER_POLL_INTERVAL: int = 300
    KAFKA_BROKERS: str = "localhost:9092"

    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def get_secret(self, key: str) -> str:
        """
        Retrieve a secret value. When DAPR_ENABLED=true, fetches from the Dapr
        secrets store (localsecrets component). Falls back to environment variable.
        """
        if self.DAPR_ENABLED:
            try:
                import httpx
                url = f"http://localhost:{self.DAPR_HTTP_PORT}/v1.0/secrets/localsecrets/{key}"
                response = httpx.get(url, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    return data.get(key, "")
            except Exception as exc:
                logger.warning(f"Dapr secret fetch failed for '{key}': {exc} — falling back to env")
        # Fallback: environment variable (case-insensitive heuristic)
        env_key = key.upper().replace("-", "_")
        return os.environ.get(env_key, "")

    def validate_jwt_secret(self) -> None:
        """
        Validate JWT secret key meets security requirements.

        Raises:
            ValueError: If JWT_SECRET_KEY is too short or insecure
        """
        if len(self.JWT_SECRET_KEY) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be at least 32 characters long for security. "
                "Generate a secure key with: openssl rand -hex 32"
            )

        # Check for common insecure values
        insecure_values = [
            "your-secret-key-here",
            "secret",
            "password",
            "changeme",
            "your-secret-key-here-minimum-32-characters"
        ]
        if self.JWT_SECRET_KEY.lower() in insecure_values:
            raise ValueError(
                "JWT_SECRET_KEY is using an insecure default value. "
                "Generate a secure key with: openssl rand -hex 32"
            )

    def get_jwt_expiration_seconds(self) -> int:
        """
        Get JWT expiration time in seconds.

        Returns:
            int: Expiration time in seconds
        """
        return self.JWT_EXPIRATION_HOURS * 3600


# Global settings instance
# This will be imported by other modules
settings = Settings()

# Validate JWT secret on startup
settings.validate_jwt_secret()

"""Application configuration management using Pydantic Settings"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://sales_user:sales_password@localhost:5432/sales_db",
        description="PostgreSQL database URL"
    )

    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )

    # Celery Configuration
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0",
        description="Celery result backend URL"
    )

    # Application Configuration
    APP_NAME: str = Field(default="Sales Analytics API", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # File Upload Configuration
    MAX_UPLOAD_SIZE: int = Field(
        default=524288000,  # 500MB
        description="Maximum upload file size in bytes"
    )
    UPLOAD_DIR: str = Field(
        default="/app/uploads",
        description="Directory for temporary file uploads"
    )

    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )

    # API Configuration
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 path prefix")
    PORT: int = Field(default=8000, description="Server port")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

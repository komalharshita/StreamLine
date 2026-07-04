import os
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables using Pydantic v2."""

    PROJECT_NAME: str = "StreamLine"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    LOG_LEVEL: str = "info"
    API_V1_STR: str = "/api/v1"

    # Server Bindings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Google Cloud Platform Settings
    GOOGLE_CLOUD_PROJECT: str = "streamline-ai-saas"
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    GCS_BUCKET_NAME: str = "streamline-data-ingestion"
    BIGQUERY_DATASET: str = "streamline_analytics"

    # Gemini API Settings
    GEMINI_API_KEY: str = ""

    # Firebase Authentication
    FIREBASE_PROJECT_ID: str = "streamline-auth"
    FIREBASE_MOCK_AUTH: bool = True

    # CORS Configurations
    # List of allowed origins, e.g., ["http://localhost:3000"]
    ALLOWED_ORIGINS: list[str] = ["*"]

    # Configure Pydantic to read from .env if present
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Instantiate settings singleton
settings = Settings()

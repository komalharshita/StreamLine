import os
import sys
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Automatically bridge Windows certificate store to gRPC SSL trust chain
if sys.platform.startswith("win"):
    try:
        import certifi

        # Set GRPC_DEFAULT_SSL_ROOTS_FILE_PATH pointing to certifi bundle (which is patched by pip-system-certs)
        os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = certifi.where()
        # Set SSL_CERT_FILE and REQUESTS_CA_BUNDLE to align standard requests and client libs
        os.environ["SSL_CERT_FILE"] = certifi.where()
        os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
    except ImportError:
        pass


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
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "https://streamline-ui.vercel.app",
        "https://stream-line-ui-architecture.vercel.app",
    ]

    # Configure Pydantic to read from .env if present
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Instantiate settings singleton
settings = Settings()

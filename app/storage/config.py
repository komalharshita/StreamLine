import logging

from app.core.config import settings
from app.storage.exceptions import StorageConfigurationError

logger = logging.getLogger("app.storage.config")


class GCSConfig:
    """Helper class loading and validating specific Google Cloud Storage settings."""

    def __init__(self) -> None:
        self.bucket_name = settings.GCS_BUCKET_NAME
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS

    def validate(self) -> None:
        """Validates that all critical settings are present.

        Raises StorageConfigurationError if bucket name is missing.
        """
        logger.debug("Validating GCS configuration variables.")
        if not self.bucket_name:
            logger.error("GCS configuration error: GCS_BUCKET_NAME is not set.")
            raise StorageConfigurationError(
                "GCS configuration failed: GCS_BUCKET_NAME environment variable is not configured."
            )

        if not self.project_id:
            logger.error("GCS configuration error: GOOGLE_CLOUD_PROJECT is not set.")
            raise StorageConfigurationError(
                "GCS configuration failed: GOOGLE_CLOUD_PROJECT environment variable is not configured."
            )


# Config instance singleton
storage_config = GCSConfig()

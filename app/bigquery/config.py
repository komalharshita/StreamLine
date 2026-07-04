import logging
from app.core.config import settings
from app.bigquery.exceptions import BigQueryConfigurationError

logger = logging.getLogger("app.bigquery.config")


class BigQueryConfig:
    """Configuration validator helper for BigQuery settings."""

    def __init__(self) -> None:
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        self.default_dataset = settings.BIGQUERY_DATASET or "streamline_analytics"

    def validate(self) -> None:
        """Validates critical settings.

        Raises BigQueryConfigurationError if configuration values are missing.
        """
        logger.debug("Validating BigQuery environment config.")
        if not self.project_id:
            logger.error("BigQuery config error: GOOGLE_CLOUD_PROJECT is not set.")
            raise BigQueryConfigurationError(
                "BigQuery configuration failed: GOOGLE_CLOUD_PROJECT is not configured."
            )


# Singleton settings instance
bq_config = BigQueryConfig()

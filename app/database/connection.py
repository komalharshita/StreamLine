import logging
from typing import Optional

from google.cloud import bigquery, storage
from google.oauth2 import service_account

from app.core.config import settings

logger = logging.getLogger("app.database.connection")


class GCPClientFactory:
    """Factory class to create and manage thread-safe Google Cloud Service Clients."""

    def __init__(self) -> None:
        self._bigquery_client: Optional[bigquery.Client] = None
        self._storage_client: Optional[storage.Client] = None
        self._credentials: Optional[service_account.Credentials] = None
        self._init_credentials()

    def _init_credentials(self) -> None:
        """Initializes service account credentials if paths are explicitly set in settings."""
        cred_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        if cred_path:
            try:
                self._credentials = (
                    service_account.Credentials.from_service_account_file(cred_path)
                )
                logger.info(f"Loaded GCP credentials from path: {cred_path}")
            except Exception as e:
                logger.error(
                    f"Failed to load GCP credentials from path {cred_path}: {str(e)}"
                )
                # Let client fall back to default credentials (ADCs)

    def get_bigquery_client(self) -> bigquery.Client:
        """Returns a singleton BigQuery client instance.

        Initializes a new client if none exists.
        """
        if self._bigquery_client is None:
            try:
                kwargs = {}
                if self._credentials:
                    kwargs["credentials"] = self._credentials
                kwargs["project"] = settings.GOOGLE_CLOUD_PROJECT

                self._bigquery_client = bigquery.Client(**kwargs)
                logger.info("BigQuery client initialized successfully.")
            except Exception as e:
                logger.critical(f"Failed to initialize BigQuery client: {str(e)}")
                raise ConnectionError("BigQuery connection failed.") from e

        return self._bigquery_client

    def get_storage_client(self) -> storage.Client:
        """Returns a singleton Google Cloud Storage client instance.

        Initializes a new client if none exists.
        """
        if self._storage_client is None:
            try:
                kwargs = {}
                if self._credentials:
                    kwargs["credentials"] = self._credentials
                kwargs["project"] = settings.GOOGLE_CLOUD_PROJECT

                self._storage_client = storage.Client(**kwargs)
                logger.info("Google Cloud Storage client initialized successfully.")
            except Exception as e:
                logger.critical(f"Failed to initialize GCS client: {str(e)}")
                raise ConnectionError("GCS connection failed.") from e

        return self._storage_client


# Instantiate client factory singleton
gcp_client_factory = GCPClientFactory()

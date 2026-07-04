import logging
from typing import Optional
from google.cloud import storage
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPIError
from google.api_core.retry import Retry

from app.storage.config import storage_config
from app.storage.exceptions import (
    StorageConnectionError,
    StorageUploadError,
    StorageDeleteError,
)

logger = logging.getLogger("app.storage.gcs_service")

# Configure a default retry policy for transient GCS errors
gcs_retry_policy = Retry(
    initial=1.0,  # 1 second initial delay
    maximum=10.0,  # 10 seconds maximum delay
    multiplier=2.0,  # Exponential backoff multiplier
    deadline=30.0,  # Stop retrying after 30 seconds
)
GCS_TIMEOUT_SECONDS = 15.0  # Timeout for GCS operations


class GCSService:
    """Production-ready client adapter for Google Cloud Storage."""

    def __init__(self) -> None:
        self.config = storage_config
        self._client: Optional[storage.Client] = None

    def _get_client(self) -> storage.Client:
        """Lazily initializes and returns the thread-safe storage Client."""
        if self._client is not None:
            return self._client

        # Validate configuration variables
        self.config.validate()

        try:
            kwargs = {}
            if self.config.credentials_path:
                logger.info(
                    f"Initializing GCS Client using service account path: {self.config.credentials_path}"
                )
                credentials = service_account.Credentials.from_service_account_file(
                    self.config.credentials_path
                )
                kwargs["credentials"] = credentials
            else:
                logger.info(
                    "Initializing GCS Client using Application Default Credentials (ADC) / IAM Role."
                )

            kwargs["project"] = self.config.project_id
            self._client = storage.Client(**kwargs)
            return self._client
            
        except Exception as e:
            logger.critical(f"Failed to connect to Google Cloud Storage client: {str(e)}", exc_info=True)
            raise StorageConnectionError(
                "Could not connect to Google Cloud Storage. Authentications or permissions failed.",
                original_exception=e,
            )

    def upload_bytes(
        self,
        blob_name: str,
        data: bytes,
        content_type: str,
        bucket_name: Optional[str] = None,
    ) -> str:
        """Uploads raw binary bytes to a GCS bucket.

        Applies exponential backoff retries and timeouts.
        Returns the public HTTPS URL to download the blob.
        """
        client = self._get_client()
        target_bucket = bucket_name or self.config.bucket_name
        logger.info(f"Initiating upload of blob: '{blob_name}' to GCS bucket: '{target_bucket}'")

        try:
            bucket = client.bucket(target_bucket)
            blob = bucket.blob(blob_name)
            
            # Perform upload with retry policy and custom timeout
            blob.upload_from_string(
                data,
                content_type=content_type,
                timeout=GCS_TIMEOUT_SECONDS,
                retry=gcs_retry_policy,
            )
            
            # Format and return the public storage URL
            public_url = blob.public_url
            logger.info(f"Successfully uploaded blob to GCS. Location URL: {public_url}")
            return public_url

        except GoogleAPIError as e:
            logger.error(f"GCS API Error during upload of blob '{blob_name}': {str(e)}", exc_info=True)
            raise StorageUploadError(
                f"Failed to upload file '{blob_name}' to GCS bucket: {str(e)}",
                original_exception=e,
            )
        except Exception as e:
            logger.error(f"Unexpected error during GCS upload of blob '{blob_name}': {str(e)}", exc_info=True)
            raise StorageUploadError(
                f"Unexpected storage error uploading file '{blob_name}': {str(e)}",
                original_exception=e,
            )

    def delete_blob(self, blob_name: str, bucket_name: Optional[str] = None) -> None:
        """Deletes a blob from GCS."""
        client = self._get_client()
        target_bucket = bucket_name or self.config.bucket_name
        logger.info(f"Initiating deletion of blob: '{blob_name}' from GCS bucket: '{target_bucket}'")

        try:
            bucket = client.bucket(target_bucket)
            blob = bucket.blob(blob_name)
            
            if blob.exists(timeout=GCS_TIMEOUT_SECONDS):
                blob.delete(timeout=GCS_TIMEOUT_SECONDS, retry=gcs_retry_policy)
                logger.info(f"Successfully deleted blob '{blob_name}' from GCS.")
            else:
                logger.warning(f"GCS delete notice: Blob '{blob_name}' does not exist in bucket.")

        except GoogleAPIError as e:
            logger.error(f"GCS API Error during deletion of blob '{blob_name}': {str(e)}", exc_info=True)
            raise StorageDeleteError(
                f"Failed to delete file '{blob_name}' from GCS bucket: {str(e)}",
                original_exception=e,
            )
        except Exception as e:
            logger.error(f"Unexpected error during GCS deletion of blob '{blob_name}': {str(e)}", exc_info=True)
            raise StorageDeleteError(
                f"Unexpected storage error deleting file '{blob_name}': {str(e)}",
                original_exception=e,
            )


# Singleton service instance
gcs_storage_service = GCSService()

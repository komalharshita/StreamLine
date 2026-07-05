import logging
from typing import Optional

from google.cloud import storage

from app.database.connection import gcp_client_factory

logger = logging.getLogger("app.database.storage")


class StorageManager:
    """Wrapper class managing interaction with Google Cloud Storage Buckets."""

    def __init__(self, client: storage.Client = None) -> None:
        # Allow passing mock/test client, fall back to factory
        self.client = client or gcp_client_factory.get_storage_client()

    def upload_file_from_memory(
        self,
        bucket_name: str,
        blob_name: str,
        data: bytes,
        content_type: Optional[str] = None,
    ) -> str:
        """Uploads a file directly from memory (bytes) to a GCS bucket.

        Returns the public URL of the uploaded blob.
        """
        logger.info(f"Uploading file to GCS: gs://{bucket_name}/{blob_name}")
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_string(data, content_type=content_type)
            return blob.public_url
        except Exception as e:
            logger.error(f"GCS Upload failed for blob {blob_name}: {str(e)}")
            raise e

    def download_file_to_memory(self, bucket_name: str, blob_name: str) -> bytes:
        """Downloads a blob's contents from a GCS bucket into memory (bytes)."""
        logger.info(f"Downloading file from GCS: gs://{bucket_name}/{blob_name}")
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            return blob.download_as_bytes()
        except Exception as e:
            logger.error(f"GCS Download failed for blob {blob_name}: {str(e)}")
            raise e

    def delete_file(self, bucket_name: str, blob_name: str) -> None:
        """Deletes a blob from a GCS bucket."""
        logger.info(f"Deleting blob from GCS: gs://{bucket_name}/{blob_name}")
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.delete()
        except Exception as e:
            logger.error(f"GCS Delete failed for blob {blob_name}: {str(e)}")
            raise e

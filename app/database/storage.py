import logging
import os
from typing import Optional

from google.cloud import storage

from app.database.connection import gcp_client_factory

logger = logging.getLogger("app.database.storage")


class StorageManager:
    """Wrapper class managing interaction with Google Cloud Storage Buckets with Local Dev Fallback."""

    def __init__(self, client: storage.Client = None) -> None:
        self.use_fallback = False
        self.client = None

        if client is not None:
            self.client = client
        else:
            try:
                self.client = gcp_client_factory.get_storage_client()
            except Exception as e:
                logger.warning(
                    f"GCS Storage client connection offline/unconfigured ({str(e)}). Falling back to local filesystem storage."
                )
                self.use_fallback = True

    def upload_file_from_memory(
        self,
        bucket_name: str,
        blob_name: str,
        data: bytes,
        content_type: Optional[str] = None,
    ) -> str:
        """Uploads a file directly from memory (bytes) to GCS (or local filesystem if fallback).

        Returns the public URL/path of the uploaded file.
        """
        if self.use_fallback:
            # Save locally under public/storage/
            local_path = os.path.join("public", "storage", blob_name.replace("/", os.sep))
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            logger.info(f"Uploading file to local disk: {local_path}")
            try:
                with open(local_path, "wb") as f:
                    f.write(data)
                # Return static URL path served by webserver
                return f"/storage/{blob_name}"
            except Exception as e:
                logger.error(f"Local storage write failed: {str(e)}")
                raise e

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
        """Downloads file contents from GCS (or local filesystem if fallback) into memory (bytes)."""
        if self.use_fallback:
            local_path = os.path.join("public", "storage", blob_name.replace("/", os.sep))
            logger.info(f"Downloading file from local disk: {local_path}")
            try:
                with open(local_path, "rb") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Local storage read failed: {str(e)}")
                raise e

        logger.info(f"Downloading file from GCS: gs://{bucket_name}/{blob_name}")
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            return blob.download_as_bytes()
        except Exception as e:
            logger.error(f"GCS Download failed for blob {blob_name}: {str(e)}")
            raise e

    def delete_file(self, bucket_name: str, blob_name: str) -> None:
        """Deletes a file from GCS (or local filesystem if fallback)."""
        if self.use_fallback:
            local_path = os.path.join("public", "storage", blob_name.replace("/", os.sep))
            logger.info(f"Deleting file from local disk: {local_path}")
            try:
                if os.path.exists(local_path):
                    os.remove(local_path)
                return
            except Exception as e:
                logger.error(f"Local storage delete failed: {str(e)}")
                raise e

        logger.info(f"Deleting blob from GCS: gs://{bucket_name}/{blob_name}")
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.delete()
        except Exception as e:
            logger.error(f"GCS Delete failed for blob {blob_name}: {str(e)}")
            raise e


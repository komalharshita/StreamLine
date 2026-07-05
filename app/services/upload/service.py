import logging
import uuid
from abc import ABC, abstractmethod
from typing import Sequence

from app.models.domain import FileMetadata
from app.repositories.storage_repository import (
    FileMetadataRepositoryInterface,
    StorageRepositoryInterface,
)
from app.schemas.upload import IngestionResponse
from app.services.base import BaseService

logger = logging.getLogger("app.services.upload")


class UploadServiceInterface(BaseService, ABC):
    """Interface managing datasets ingestion and file uploads."""

    @abstractmethod
    def handle_upload(
        self, filename: str, content_type: str, data: bytes, user_id: str
    ) -> FileMetadata:
        """Uploads file to object storage and writes metadata record."""
        pass

    @abstractmethod
    def trigger_ingestion(self, file_id: str, target_table: str) -> IngestionResponse:
        """Ingests file contents from GCS bucket into BigQuery table."""
        pass

    @abstractmethod
    def list_user_files(self) -> Sequence[FileMetadata]:
        """Lists all uploaded file metadata logs."""
        pass


class UploadService(UploadServiceInterface):
    """Concrete implementation of UploadService."""

    def __init__(
        self,
        metadata_repo: FileMetadataRepositoryInterface,
        storage_repo: StorageRepositoryInterface,
    ) -> None:
        self.metadata_repo = metadata_repo
        self.storage_repo = storage_repo

    def handle_upload(
        self, filename: str, content_type: str, data: bytes, user_id: str
    ) -> FileMetadata:
        logger.info(f"Handling upload for file: {filename} by user: {user_id}")
        file_id = str(uuid.uuid4())
        blob_name = f"uploads/{user_id}/{file_id}_{filename}"

        # Upload blob content to cloud storage
        public_url = self.storage_repo.upload_blob(blob_name, data, content_type)
        gcs_uri = (
            f"gs://{self.storage_repo.bucket_name}/{blob_name}"
            if hasattr(self.storage_repo, "bucket_name")
            else f"gs://streamline-data-ingestion/{blob_name}"
        )

        # Save metadata transaction log
        metadata = FileMetadata(
            id=file_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            gcs_uri=gcs_uri,
            public_url=public_url,
            uploaded_by=user_id,
            processed=False,
        )
        return self.metadata_repo.save(metadata)

    def trigger_ingestion(self, file_id: str, target_table: str) -> IngestionResponse:
        logger.info(
            f"Triggering BigQuery ingestion for file: {file_id} to table: {target_table}"
        )
        metadata = self.metadata_repo.get_by_id(file_id)
        if not metadata:
            raise ValueError(f"File metadata record not found for ID: {file_id}")

        # Simulate BigQuery Load Job
        job_id = f"bq-load-{uuid.uuid4()}"
        logger.info(f"Simulating BigQuery load job {job_id} from {metadata.gcs_uri}")

        # Mark metadata file as processed
        metadata.processed = True
        self.metadata_repo.save(metadata)

        return IngestionResponse(
            job_id=job_id,
            status="SUCCESS",
            rows_loaded=1500,  # Simulated loaded rows
            message=f"Successfully loaded data from {metadata.filename} into BigQuery table {target_table}.",
        )

    def list_user_files(self) -> Sequence[FileMetadata]:
        return self.metadata_repo.list_all()

import logging
from abc import ABC, abstractmethod
from typing import Optional, Sequence

from app.database.bigquery import BigQueryManager
from app.database.storage import StorageManager
from app.models.domain import FileMetadata
from app.repositories.base import BaseRepository

logger = logging.getLogger("app.repositories.storage")


class FileMetadataRepositoryInterface(BaseRepository[FileMetadata], ABC):
    """Interface for saving and retrieving uploaded file metadata logs."""

    @abstractmethod
    def list_unprocessed(self) -> Sequence[FileMetadata]:
        """Lists files that have been uploaded but not yet ingested/processed into BigQuery."""
        pass


class StorageRepositoryInterface(ABC):
    """Interface for direct raw binary storage blob transactions (GCS)."""

    @abstractmethod
    def upload_blob(
        self, blob_name: str, data: bytes, content_type: Optional[str] = None
    ) -> str:
        """Uploads raw binary bytes to cloud storage and returns target URL."""
        pass

    @abstractmethod
    def download_blob(self, blob_name: str) -> bytes:
        """Downloads raw binary bytes from cloud storage."""
        pass

    @abstractmethod
    def delete_blob(self, blob_name: str) -> None:
        """Removes a blob from cloud storage."""
        pass


class GCSStorageRepository(StorageRepositoryInterface):
    """Concrete implementation of Cloud Storage Blob storage using StorageManager."""

    def __init__(self, storage_manager: StorageManager, bucket_name: str) -> None:
        self.storage_manager = storage_manager
        self.bucket_name = bucket_name

    def upload_blob(
        self, blob_name: str, data: bytes, content_type: Optional[str] = None
    ) -> str:
        logger.info(f"Uploading blob {blob_name} to bucket {self.bucket_name}")
        return self.storage_manager.upload_file_from_memory(
            self.bucket_name, blob_name, data, content_type
        )

    def download_blob(self, blob_name: str) -> bytes:
        logger.info(f"Downloading blob {blob_name} from bucket {self.bucket_name}")
        return self.storage_manager.download_file_to_memory(
            self.bucket_name, blob_name
        )

    def delete_blob(self, blob_name: str) -> None:
        logger.info(f"Deleting blob {blob_name} from bucket {self.bucket_name}")
        self.storage_manager.delete_file(self.bucket_name, blob_name)


class BigQueryFileMetadataRepository(FileMetadataRepositoryInterface):
    """Concrete metadata tracker storing file states in BigQuery metadata tables."""

    def __init__(self, bq_manager: BigQueryManager) -> None:
        self.bq_manager = bq_manager
        self.dataset = "streamline_metadata"
        self.table = "file_uploads"

    def get_by_id(self, id: str) -> Optional[FileMetadata]:
        logger.info(f"Fetching metadata for file {id}")
        query = f"SELECT * FROM `{self.dataset}.{self.table}` WHERE id = '{id}' LIMIT 1"
        try:
            results = self.bq_manager.execute_query(query)
            for row in results:
                return FileMetadata.model_validate(dict(row))
        except Exception as e:
            logger.error(f"Error fetching file metadata by ID: {str(e)}")
        return None

    def list_all(self) -> Sequence[FileMetadata]:
        logger.info("Listing all file metadata records")
        query = f"SELECT * FROM `{self.dataset}.{self.table}` ORDER BY uploaded_at DESC"
        files = []
        try:
            results = self.bq_manager.execute_query(query)
            for row in results:
                files.append(FileMetadata.model_validate(dict(row)))
        except Exception as e:
            logger.error(f"Error listing file metadata: {str(e)}")
        return files

    def list_unprocessed(self) -> Sequence[FileMetadata]:
        logger.info("Listing unprocessed uploaded files")
        query = f"SELECT * FROM `{self.dataset}.{self.table}` WHERE processed = FALSE ORDER BY uploaded_at ASC"
        files = []
        try:
            results = self.bq_manager.execute_query(query)
            for row in results:
                files.append(FileMetadata.model_validate(dict(row)))
        except Exception as e:
            logger.error(f"Error listing unprocessed metadata: {str(e)}")
        return files

    def save(self, entity: FileMetadata) -> FileMetadata:
        logger.info(f"Saving file metadata {entity.id} to metadata table")
        row = [entity.model_dump(mode="json")]
        errors = self.bq_manager.insert_rows_json(self.dataset, self.table, row)
        if errors:
            raise RuntimeError(f"Failed to save file metadata: {errors}")
        return entity

    def delete_by_id(self, id: str) -> None:
        logger.info(f"Deleting file metadata record {id}")
        query = f"DELETE FROM `{self.dataset}.{self.table}` WHERE id = '{id}'"
        self.bq_manager.execute_query(query)

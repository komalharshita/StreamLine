import logging
from datetime import datetime, timezone
from hashlib import sha256
from threading import Lock
from typing import Any, Optional

logger = logging.getLogger("app.upload.metadata_service")


class MetadataService:
    """Thread-safe in-memory database adapter tracking file metadata records and hashes."""

    def __init__(self) -> None:
        self._lock = Lock()
        # Storage dictionary: upload_id -> metadata dictionary
        self._store: dict[str, dict[str, Any]] = {}
        # Index dictionary for duplicate prevention: sha256_hash -> upload_id
        self._hash_index: dict[str, str] = {}

    @staticmethod
    def calculate_hash(file_bytes: bytes) -> str:
        """Calculates the SHA-256 hash checksum of file bytes to detect duplicate content."""
        hasher = sha256()
        # Read in chunks of 64KB
        chunk_size = 64 * 1024
        for i in range(0, len(file_bytes), chunk_size):
            hasher.update(file_bytes[i : i + chunk_size])
        return hasher.hexdigest()

    def check_duplicate_hash(self, file_hash: str) -> Optional[dict[str, Any]]:
        """Checks if a file with the same checksum has already been uploaded.

        Returns the matched metadata record if found, else None.
        """
        with self._lock:
            upload_id = self._hash_index.get(file_hash)
            if upload_id and upload_id in self._store:
                record = self._store[upload_id]
                # Double check status is not deleted
                if record.get("status") != "deleted":
                    return record
        return None

    def save(
        self,
        upload_id: str,
        filename: str,
        extension: str,
        rows: int,
        columns: int,
        size_bytes: int,
        file_hash: str,
        uploaded_by: str,
        gcs_uri: Optional[str] = None,
        gcs_url: Optional[str] = None,
        dataset: Optional[str] = None,
        table: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Saves a new upload metadata record and updates the duplicate index."""
        record = {
            "upload_id": upload_id,
            "filename": filename,
            "extension": extension,
            "rows": rows,
            "columns": columns,
            "size_bytes": size_bytes,
            "file_hash": file_hash,
            "upload_time": datetime.now(timezone.utc),
            "uploaded_by": uploaded_by,
            "gcs_uri": gcs_uri,
            "gcs_url": gcs_url,
            "dataset": dataset,
            "table": table,
            "job_id": job_id,
            "status": "uploaded",
        }
        
        with self._lock:
            self._store[upload_id] = record
            self._hash_index[file_hash] = upload_id
            logger.info(f"Metadata record saved for upload ID: {upload_id}")
            
        return record

    def get_by_id(self, upload_id: str) -> Optional[dict[str, Any]]:
        """Retrieves a single upload metadata record by ID."""
        with self._lock:
            record = self._store.get(upload_id)
            if record and record.get("status") != "deleted":
                return record
        return None

    def list_all(self) -> list[dict[str, Any]]:
        """Lists all active (non-deleted) upload metadata records."""
        with self._lock:
            return [
                record
                for record in self._store.values()
                if record.get("status") != "deleted"
            ]

    def delete_by_id(self, upload_id: str) -> bool:
        """Soft-deletes an upload record (removes from active storage, keeps hash index)."""
        with self._lock:
            if upload_id in self._store:
                record = self._store[upload_id]
                if record.get("status") != "deleted":
                    record["status"] = "deleted"
                    # Remove from hash index so same file can be re-uploaded later if deleted
                    file_hash = record.get("file_hash")
                    if file_hash and self._hash_index.get(file_hash) == upload_id:
                        self._hash_index.pop(file_hash, None)
                    logger.info(f"Metadata record soft-deleted for ID: {upload_id}")
                    return True
        return False


# Singleton metadata store instance
metadata_store = MetadataService()

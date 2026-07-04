import logging
import uuid
from typing import Any, Optional
from fastapi import HTTPException, status

from app.upload.file_parser import FileParser
from app.upload.metadata_service import metadata_store
from app.upload.validators import FileValidator

logger = logging.getLogger("app.upload.upload_service")


class UploadService:
    """Service class orchestrating the validations, duplicate checking, parsing, and storage mapping."""

    @staticmethod
    def process_upload(
        filename: str,
        content_type: str,
        file_bytes: bytes,
        uploaded_by: str,
    ) -> dict[str, Any]:
        """Validates, deduplicates, parses, and logs the metadata of an uploaded file."""
        size_bytes = len(file_bytes)
        logger.info(f"Processing upload for file: '{filename}', size={size_bytes} bytes, MIME={content_type}")

        # 1. Validate File Size (0 bytes check, 100MB limit check)
        FileValidator.validate_size(size_bytes)

        # 2. Validate File Format & Extension MIME alignment
        extension = FileValidator.validate_format(filename, content_type)

        # 3. Calculate content checksum
        file_hash = metadata_store.calculate_hash(file_bytes)

        # 4. Check for duplicate upload
        duplicate = metadata_store.check_duplicate_hash(file_hash)
        if duplicate:
            dup_id = duplicate["upload_id"]
            logger.warning(f"File upload rejected: Duplicate content detected. Existing Upload ID: {dup_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "File upload rejected: A file with identical contents has already been uploaded.",
                    "existing_upload_id": dup_id,
                    "filename": duplicate["filename"],
                    "upload_time": duplicate["upload_time"].isoformat(),
                },
            )

        # 5. Parse file structure dimensions (rows, columns) - catches corruption errors
        rows, columns = FileParser.parse_and_get_dimensions(file_bytes, extension)

        # 6. Save metadata
        upload_id = str(uuid.uuid4())
        metadata_record = metadata_store.save(
            upload_id=upload_id,
            filename=filename,
            extension=extension,
            rows=rows,
            columns=columns,
            size_bytes=size_bytes,
            file_hash=file_hash,
            uploaded_by=uploaded_by,
        )

        return metadata_record

    @staticmethod
    def get_upload(upload_id: str) -> dict[str, Any]:
        """Retrieves file upload metadata by UUID."""
        record = metadata_store.get_by_id(upload_id)
        if not record:
            logger.warning(f"Metadata lookup failed: Upload ID '{upload_id}' not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File upload with ID '{upload_id}' not found.",
            )
        return record

    @staticmethod
    def list_uploads() -> list[dict[str, Any]]:
        """Lists all active uploads."""
        return metadata_store.list_all()

    @staticmethod
    def delete_upload(upload_id: str) -> None:
        """Deletes upload records from the catalog."""
        success = metadata_store.delete_by_id(upload_id)
        if not success:
            logger.warning(f"Delete operation failed: Upload ID '{upload_id}' not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File upload with ID '{upload_id}' not found.",
            )

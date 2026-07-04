import logging
import os
from typing import Optional
from fastapi import HTTPException, status

logger = logging.getLogger("app.upload.validators")

# Validation Constants
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MIME_TYPE_MAPPING = {
    "text/csv": {".csv"},
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {".xlsx"},
    "application/vnd.ms-excel": {".xls", ".xlsx"},
    "application/octet-stream": {".csv", ".xlsx", ".xls"},  # Generic fallbacks
}


class FileValidator:
    """Validator class for checking file formats, sizes, empty payloads, and MIME alignments."""

    @staticmethod
    def validate_size(size_bytes: int) -> None:
        """Validates file size is within limits and is not empty."""
        logger.debug(f"Validating file size: {size_bytes} bytes")
        
        if size_bytes == 0:
            logger.warning("Upload validation failed: File is empty.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File upload rejected: The uploaded file is empty (0 bytes).",
            )
            
        if size_bytes > MAX_FILE_SIZE_BYTES:
            logger.warning(
                f"Upload validation failed: File size {size_bytes} exceeds maximum {MAX_FILE_SIZE_BYTES}."
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File upload rejected: File size exceeds the maximum limit of 100 MB.",
            )

    @staticmethod
    def validate_format(filename: str, content_type: Optional[str] = None) -> str:
        """Validates extension is supported and aligns with MIME content type."""
        # Extract extension
        _, ext = os.path.splitext(filename.lower())
        logger.debug(f"Validating file format: extension={ext}, MIME={content_type}")

        if ext not in ALLOWED_EXTENSIONS:
            logger.warning(f"Upload validation failed: Extension {ext} is not allowed.")
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=(
                    f"File upload rejected: Format '{ext}' is not supported. "
                    f"Only CSV (.csv) and Excel (.xlsx, .xls) files are allowed."
                ),
            )

        # Optional content-type check alignment if provided
        if content_type:
            content_type = content_type.lower().strip()
            # If the content-type is registered, verify extension alignment
            if content_type in MIME_TYPE_MAPPING:
                allowed_exts = MIME_TYPE_MAPPING[content_type]
                if ext not in allowed_exts:
                    logger.warning(
                        f"Upload validation failed: MIME type {content_type} does not align with extension {ext}."
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"File upload rejected: File extension '{ext}' does not match "
                            f"the declared content MIME type '{content_type}'."
                        ),
                    )
            else:
                # Basic media check for generic file types like PDFs, Images, Word, etc.
                if content_type.startswith(("image/", "audio/", "video/", "application/pdf", "application/msword")):
                    logger.warning(f"Upload validation failed: Explicitly rejected MIME type {content_type}.")
                    raise HTTPException(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail="File upload rejected: Unsupported document, image, or media format.",
                    )

        return ext

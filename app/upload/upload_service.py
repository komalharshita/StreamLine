import logging
import uuid
from typing import Any, Optional
from fastapi import HTTPException, status

from app.upload.file_parser import FileParser
from app.upload.metadata_service import metadata_store
from app.upload.validators import FileValidator
from app.storage.gcs_service import gcs_storage_service
from app.bigquery.bigquery_service import bq_ingestion_service

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
        rows, columns, df = FileParser.parse_and_get_dimensions(file_bytes, extension)

        # 6. Upload original file to Cloud Storage
        upload_id = str(uuid.uuid4())
        blob_name = f"uploads/{uploaded_by}/{upload_id}_{filename}"
        
        try:
            gcs_url = gcs_storage_service.upload_bytes(
                blob_name=blob_name,
                data=file_bytes,
                content_type=content_type
            )
            gcs_uri = f"gs://{gcs_storage_service.config.bucket_name}/{blob_name}"
        except Exception as e:
            logger.critical(f"Upload to GCS failed: {str(e)}")
            raise e

        # 6b. Ingest DataFrame into Google BigQuery
        workspace = "analytics"
        if "@" in uploaded_by:
            workspace = uploaded_by.split("@")[-1].split(".")[0]

        try:
            bq_result = bq_ingestion_service.load_dataframe(df=df, workspace=workspace)
            dataset = bq_result["dataset"]
            table = bq_result["table"]
            job_id = bq_result["job_id"]
        except Exception as e:
            logger.critical(f"BigQuery ingestion failed: {str(e)}")
            raise e

        # 7. Save metadata including GCS and BigQuery fields
        metadata_record = metadata_store.save(
            upload_id=upload_id,
            filename=filename,
            extension=extension,
            rows=rows,
            columns=columns,
            size_bytes=size_bytes,
            file_hash=file_hash,
            uploaded_by=uploaded_by,
            gcs_uri=gcs_uri,
            gcs_url=gcs_url,
            dataset=dataset,
            table=table,
            job_id=job_id,
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
        """Deletes upload records from the catalog and removes the associated GCS blob."""
        # 1. Fetch metadata to retrieve GCS URI
        record = UploadService.get_upload(upload_id)
        
        # 2. Attempt deleting the GCS blob if it exists
        gcs_uri = record.get("gcs_uri")
        if gcs_uri:
            try:
                # Extract blob name from gs://bucket_name/blob_name
                bucket_prefix = f"gs://{gcs_storage_service.config.bucket_name}/"
                if gcs_uri.startswith(bucket_prefix):
                    blob_name = gcs_uri.split(bucket_prefix)[-1]
                    gcs_storage_service.delete_blob(blob_name)
            except Exception as e:
                logger.error(f"Failed to delete GCS blob associated with upload '{upload_id}': {str(e)}")
                # Continue soft deleting metadata even if GCS deletion fails to keep states synchronized
        
        # 3. Perform soft delete from catalog
        success = metadata_store.delete_by_id(upload_id)
        if not success:
            logger.warning(f"Delete operation failed: Upload ID '{upload_id}' not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File upload with ID '{upload_id}' not found.",
            )

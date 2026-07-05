import logging
import uuid
from typing import Any

from fastapi import BackgroundTasks, HTTPException, status

from app.bigquery.bigquery_service import bq_ingestion_service
from app.cleaning.cleaning_service import cleaning_service
from app.cleaning.schemas import CleaningConfig
from app.cleaning.validators import CleaningValidator
from app.storage.gcs_service import gcs_storage_service
from app.upload.analyzer import DatasetAnalyzer
from app.upload.file_parser import FileParser
from app.upload.metadata_service import metadata_store
from app.upload.status_tracker import UploadStatusTracker
from app.upload.validators import FileValidator

logger = logging.getLogger("app.upload.upload_service")

# In-memory dictionary cache to store parsed datasets between preview and confirmation
_temp_upload_store: dict[str, dict[str, Any]] = {}


class UploadService:
    """Service class orchestrating dataset validation, preview, and async ingestion workflows."""

    @staticmethod
    def generate_preview(
        filename: str,
        content_type: str,
        file_bytes: bytes,
        uploaded_by: str,
    ) -> dict[str, Any]:
        """Validates, parses, detects types, audits quality, and stores the file temporarily for confirmation."""
        size_bytes = len(file_bytes)
        upload_id = str(uuid.uuid4())

        # 1. Initialize tracking
        UploadStatusTracker.initialize_status(upload_id)

        try:
            # 2. Validate File Size
            UploadStatusTracker.update_status(upload_id, "VALIDATING", "Validating Size", 20)
            FileValidator.validate_size(size_bytes)

            # 3. Validate File Format & Extension MIME alignment
            extension = FileValidator.validate_format(filename, content_type)

            # 4. Check for duplicate upload (Deduplicate checksum)
            file_hash = metadata_store.calculate_hash(file_bytes)
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

            # 5. Parse Dataset
            UploadStatusTracker.update_status(upload_id, "PARSING", "Parsing File Stream", 45)
            rows, cols, df = FileParser.parse_and_get_dimensions(file_bytes, extension)

            # Validate DataFrame integrity (raises 400 if empty or zero columns)
            CleaningValidator.validate_dataframe(df)

            # 6. Analyze Dataset Type and Data Quality
            UploadStatusTracker.update_status(upload_id, "ANALYZING", "Analyzing Schema and Quality", 70)
            detected_type, confidence = DatasetAnalyzer.infer_dataset_type([str(c) for c in df.columns])
            quality_report = DatasetAnalyzer.generate_quality_report(df)

            # 7. Generate Preview Rows (Clean headers/NaN values)
            UploadStatusTracker.update_status(upload_id, "GENERATING_PREVIEW", "Generating Preview View", 85)
            preview_df = df.head(25).fillna("")
            preview_rows = preview_df.to_dict(orient="records")

            schema = [{"name": str(col), "type": str(dtype)} for col, dtype in df.dtypes.items()]

            statistics = {
                "total_rows": rows,
                "total_columns": cols,
                "file_size_bytes": size_bytes,
                "delimiter": "," if extension == ".csv" else "Excel Format",
                "encoding": "utf-8",
                "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB",
                "missing_values": df.isnull().sum().to_dict(),
                "duplicate_rows": int(df.duplicated().sum()),
                "dtypes": {str(col): str(dtype) for col, dtype in df.dtypes.items()},
                "null_percentage": {str(col): float((df[col].isnull().sum() / max(1, rows)) * 100) for col in df.columns},
                "detected_type": detected_type,
                "confidence": confidence,
                "quality_score": quality_report["quality_score"],
                "quality_report": quality_report,
            }

            # 8. Cache the temporary record
            _temp_upload_store[upload_id] = {
                "filename": filename,
                "content_type": content_type,
                "file_bytes": file_bytes,
                "uploaded_by": uploaded_by,
                "extension": extension,
                "file_hash": file_hash,
                "detected_type": detected_type,
                "quality_score": quality_report["quality_score"],
            }

            # 9. Set status to WAITING_CONFIRMATION
            UploadStatusTracker.update_status(
                upload_id,
                "WAITING_CONFIRMATION",
                "Awaiting Ingestion Confirmation",
                100,
            )

            return {
                "upload_id": upload_id,
                "preview_rows": preview_rows,
                "schema": schema,
                "statistics": statistics,
            }

        except Exception as ex:
            UploadStatusTracker.fail_status(upload_id, str(ex))
            raise ex

    @staticmethod
    def confirm_import(
        upload_id: str,
        background_tasks: BackgroundTasks,
        uploaded_by: str,
    ) -> dict[str, Any]:
        """Looks up the cached preview record and starts the async ingestion task."""
        cached = _temp_upload_store.get(upload_id)
        if not cached:
            logger.error(f"Confirmation failed: Temporary upload record '{upload_id}' not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File upload preview not found. It may have expired or already been imported.",
            )

        # 1. Update status to IMPORTING
        UploadStatusTracker.update_status(
            upload_id, "IMPORTING", "Importing and Preprocessing", 15
        )

        # 2. Queue Background Task
        background_tasks.add_task(
            UploadService._process_confirm_async,
            upload_id=upload_id,
            filename=cached["filename"],
            content_type=cached["content_type"],
            file_bytes=cached["file_bytes"],
            uploaded_by=uploaded_by,
            extension=cached["extension"],
            file_hash=cached["file_hash"],
            dataset_type=cached["detected_type"],
        )

        return {
            "success": True,
            "message": "Dataset confirmed. Ingestion running in the background.",
            "upload_id": upload_id,
        }

    @staticmethod
    def _process_confirm_async(
        upload_id: str,
        filename: str,
        content_type: str,
        file_bytes: bytes,
        uploaded_by: str,
        extension: str,
        file_hash: str,
        dataset_type: str,
    ) -> None:
        """Asynchronously cleans, uploads to GCS, ingests to BigQuery, and refreshes the Decision Engine."""
        logger.info(f"Asynchronously executing confirmation import for upload ID: '{upload_id}'")

        try:
            # 1. Parse into DataFrame
            _, _, df = FileParser.parse_and_get_dimensions(file_bytes, extension)

            # 2. Clean and Impute
            UploadStatusTracker.update_status(
                upload_id, "IMPORTING", "Cleaning and Normalizing", 35
            )
            config = CleaningConfig(dataset_type=dataset_type)
            df_cleaned, quality_report = cleaning_service.clean_dataset(df, config)
            cleaned_rows = len(df_cleaned)
            cleaned_cols = len(df_cleaned.columns)

            # 3. Upload raw file to Cloud Storage
            UploadStatusTracker.update_status(
                upload_id,
                "UPLOADING_TO_BIGQUERY",
                "Uploading Original file to Cloud Storage",
                55,
            )
            blob_name = f"uploads/{uploaded_by}/{upload_id}_{filename}"
            gcs_url = gcs_storage_service.upload_bytes(
                blob_name=blob_name, data=file_bytes, content_type=content_type
            )
            gcs_uri = f"gs://{gcs_storage_service.config.bucket_name}/{blob_name}"

            # 4. Ingest Cleaned Data into Google BigQuery
            UploadStatusTracker.update_status(
                upload_id,
                "UPLOADING_TO_BIGQUERY",
                "Ingesting Cleaned schema to BigQuery Database",
                75,
            )
            workspace = "analytics"
            if "@" in uploaded_by:
                workspace = uploaded_by.split("@")[-1].split(".")[0]

            bq_result = bq_ingestion_service.load_dataframe(
                df=df_cleaned, workspace=workspace
            )
            dataset = bq_result["dataset"]
            table = bq_result["table"]
            job_id = bq_result["job_id"]

            # 5. Evaluate Decision Rules
            UploadStatusTracker.update_status(
                upload_id,
                "RUNNING_DECISION_ENGINE",
                "Evaluating Priority and ROI Decision Rules",
                88,
            )
            try:
                from app.decision_engine.decision_service import decision_service
                decision_service.refresh_feed_from_dataframe(df_cleaned, dataset_type)
            except Exception as e:
                logger.error(f"Failed to refresh decision feed on confirm: {str(e)}")

            # 6. Save final Metadata Catalog record
            UploadStatusTracker.update_status(
                upload_id,
                "GENERATING_METADATA",
                "Logging Metadata Sync Catalog",
                95,
            )
            metadata_store.save(
                upload_id=upload_id,
                filename=filename,
                extension=extension,
                rows=cleaned_rows,
                columns=cleaned_cols,
                size_bytes=len(file_bytes),
                file_hash=file_hash,
                uploaded_by=uploaded_by,
                gcs_uri=gcs_uri,
                gcs_url=gcs_url,
                dataset=dataset,
                table=table,
                job_id=job_id,
                quality_score=quality_report.quality_score,
            )

            # 7. Remove from temp cache store
            _temp_upload_store.pop(upload_id, None)

            # 8. Complete
            UploadStatusTracker.update_status(upload_id, "COMPLETED", "Ready", 100)
            logger.info(f"Asynchronous ingestion successfully completed for upload ID: '{upload_id}'")

        except Exception as ex:
            logger.critical(f"Asynchronous pipeline failed for upload ID '{upload_id}': {str(ex)}")
            UploadStatusTracker.fail_status(upload_id, str(ex))

    @staticmethod
    def process_upload(
        filename: str,
        content_type: str,
        file_bytes: bytes,
        uploaded_by: str,
    ) -> dict[str, Any]:
        """Legacy synchronous endpoint wrapper matching backwards compatibility rules."""
        size_bytes = len(file_bytes)
        upload_id = str(uuid.uuid4())

        UploadStatusTracker.initialize_status(upload_id)
        try:
            # Re-use generate_preview internally for validation, parsing and metadata creation
            preview = UploadService.generate_preview(
                filename=filename,
                content_type=content_type,
                file_bytes=file_bytes,
                uploaded_by=uploaded_by,
            )

            preview_upload_id = preview["upload_id"]

            # Execute confirmation steps synchronously
            cached = _temp_upload_store.get(preview_upload_id)
            if not cached:
                raise ValueError("Seeding temporary cache failed.")

            UploadService._process_confirm_async(
                upload_id=preview_upload_id,
                filename=filename,
                content_type=content_type,
                file_bytes=file_bytes,
                uploaded_by=uploaded_by,
                extension=cached["extension"],
                file_hash=cached["file_hash"],
                dataset_type=cached["detected_type"],
            )

            return metadata_store.get_by_id(preview_upload_id) or {}

        except Exception as ex:
            UploadStatusTracker.fail_status(upload_id, str(ex))
            raise ex

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
        record = UploadService.get_upload(upload_id)
        gcs_uri = record.get("gcs_uri")
        if gcs_uri:
            try:
                bucket_prefix = f"gs://{gcs_storage_service.config.bucket_name}/"
                if gcs_uri.startswith(bucket_prefix):
                    blob_name = gcs_uri.split(bucket_prefix)[-1]
                    gcs_storage_service.delete_blob(blob_name)
            except Exception as e:
                logger.error(f"Failed to delete GCS blob associated with upload '{upload_id}': {str(e)}")

        success = metadata_store.delete_by_id(upload_id)
        if not success:
            logger.warning(f"Delete operation failed: Upload ID '{upload_id}' not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File upload with ID '{upload_id}' not found.",
            )

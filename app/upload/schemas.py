from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class UploadMetadataResponse(BaseModel):
    """Pydantic schema representing the extracted file metadata response."""

    upload_id: str = Field(
        ..., description="Unique UUID generated for the uploaded file"
    )
    filename: str = Field(..., description="Original filename of the upload")
    extension: str = Field(
        ..., description="Normalized file extension (e.g. '.csv', '.xlsx')"
    )
    rows: int = Field(..., description="Total row count extracted from the file")
    columns: int = Field(..., description="Total column count extracted from the file")
    size_bytes: int = Field(..., description="Total file size in bytes")
    upload_time: datetime = Field(
        ..., description="Timestamp of when the upload completed"
    )
    uploaded_by: str = Field(
        ..., description="Firebase identifier or email of the user"
    )
    gcs_uri: Optional[str] = Field(
        None, description="Google Cloud Storage URI path (gs://bucket/path)"
    )
    gcs_url: Optional[str] = Field(
        None, description="Public URL to access the uploaded file"
    )
    dataset: Optional[str] = Field(
        None, description="Google BigQuery dataset destination ID"
    )
    table: Optional[str] = Field(
        None, description="Google BigQuery table destination ID"
    )
    job_id: Optional[str] = Field(None, description="BigQuery Load Job Identifier")
    quality_score: Optional[float] = Field(
        None, description="Inferred dataset quality score (0-100)"
    )
    status: str = Field(
        ..., description="Liveness status of the dataset (e.g., 'uploaded', 'deleted')"
    )

    class Config:
        from_attributes = True


class UploadDeleteResponse(BaseModel):
    """Pydantic schema representing file removal status confirmation."""

    success: bool = Field(
        ..., description="Indicates if deletion was completed successfully"
    )
    message: str = Field(..., description="Explanatory text message")
    upload_id: str = Field(..., description="UUID of the deleted file")


class UploadPreviewResponse(BaseModel):
    """Payload representing dataset schema previews and statistics."""

    upload_id: str = Field(..., description="Temporary or persistent upload UUID")
    preview_rows: list[dict[str, Any]] = Field(..., description="First 25 data rows")
    schema_info: list[dict[str, Any]] = Field(..., alias="schema", description="Column names and data types")
    statistics: dict[str, Any] = Field(..., description="Calculated quality and file stats")

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        from_attributes = True


class UploadConfirmRequest(BaseModel):
    """Payload confirming background ingestion trigger."""

    upload_id: str = Field(..., description="Identifies the temporary upload storage record")


class UploadConfirmResponse(BaseModel):
    """Confirmation feedback trigger response."""

    success: bool = Field(..., description="Tells if confirmation process started successfully")
    message: str = Field(..., description="Status description")
    upload_id: str = Field(..., description="Target upload UUID")


class UploadStatusResponse(BaseModel):
    """Granular progress check status response."""

    status: str = Field(..., description="Granular state token (e.g. WAITING_CONFIRMATION)")
    stage: str = Field(..., description="Human friendly state name")
    progress: int = Field(..., description="Percentage number (0-100)")
    estimated_time_remaining: str = Field(..., description="Time estimation statement")
    elapsed_time: str = Field(..., description="Time elapsed statement")
    completed_steps: list[str] = Field(..., description="Checklist of completed stages")
    error: Optional[str] = Field(None, description="Error message description if failed")

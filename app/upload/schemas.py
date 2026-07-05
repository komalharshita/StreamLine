from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UploadMetadataResponse(BaseModel):
    """Pydantic schema representing the extracted file metadata response."""

    upload_id: str = Field(..., description="Unique UUID generated for the uploaded file")
    filename: str = Field(..., description="Original filename of the upload")
    extension: str = Field(..., description="Normalized file extension (e.g. '.csv', '.xlsx')")
    rows: int = Field(..., description="Total row count extracted from the file")
    columns: int = Field(..., description="Total column count extracted from the file")
    size_bytes: int = Field(..., description="Total file size in bytes")
    upload_time: datetime = Field(..., description="Timestamp of when the upload completed")
    uploaded_by: str = Field(..., description="Firebase identifier or email of the user")
    gcs_uri: Optional[str] = Field(None, description="Google Cloud Storage URI path (gs://bucket/path)")
    gcs_url: Optional[str] = Field(None, description="Public URL to access the uploaded file")
    dataset: Optional[str] = Field(None, description="Google BigQuery dataset destination ID")
    table: Optional[str] = Field(None, description="Google BigQuery table destination ID")
    job_id: Optional[str] = Field(None, description="BigQuery Load Job Identifier")
    quality_score: Optional[float] = Field(None, description="Inferred dataset quality score (0-100)")
    status: str = Field(..., description="Liveness status of the dataset (e.g., 'uploaded', 'deleted')")

    class Config:
        from_attributes = True


class UploadDeleteResponse(BaseModel):
    """Pydantic schema representing file removal status confirmation."""

    success: bool = Field(..., description="Indicates if deletion was completed successfully")
    message: str = Field(..., description="Explanatory text message")
    upload_id: str = Field(..., description="UUID of the deleted file")

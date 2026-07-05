from datetime import datetime

from pydantic import BaseModel, Field


class FileMetadataResponse(BaseModel):
    """Response payload detailing upload metadata."""

    id: str = Field(..., description="Unique file reference ID")
    filename: str = Field(...)
    content_type: str = Field(...)
    size_bytes: int = Field(...)
    public_url: str = Field(..., description="Secure link to download the file")
    uploaded_at: datetime = Field(...)
    processed: bool = Field(...)


class IngestionRequest(BaseModel):
    """Payload to trigger analytical data parsing/ingestion into BigQuery."""

    file_id: str = Field(..., description="Reference ID of the uploaded file")
    target_table: str = Field(..., description="BigQuery target destination table name")


class IngestionResponse(BaseModel):
    """Response confirming ingestion pipeline outcome."""

    job_id: str = Field(..., description="BigQuery Load Job Identifier")
    status: str = Field(
        ..., description="State of the load job (e.g. RUNNING, SUCCESS, FAILED)"
    )
    rows_loaded: int = Field(default=0, description="Count of records inserted")
    message: str = Field(...)

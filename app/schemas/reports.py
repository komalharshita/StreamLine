from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    """Payload to trigger report compilation and export."""

    title: str = Field(..., min_length=3, description="Display header of the report")
    query_executed: str = Field(
        ..., description="BigQuery SQL expression generating target dataset"
    )
    export_format: Literal["csv", "pdf", "json"] = Field(default="csv")


class ReportResponse(BaseModel):
    """Response payload containing generated report locations and identifiers."""

    id: str
    title: str
    query_executed: str
    export_format: str
    gcs_uri: Optional[str] = None
    download_url: Optional[str] = None
    created_by: str
    created_at: datetime
    status: str = Field(
        "ready", description="Status of compilation (ready, compiling, failed)"
    )

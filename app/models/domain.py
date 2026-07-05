from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class DomainModel(BaseModel):
    """Base domain model configured for Pydantic v2 behavior."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
    )


class User(DomainModel):
    """Domain model representing a system user."""

    id: str = Field(..., description="Unique user identifier (Firebase UID)")
    email: str = Field(..., description="User's email address")
    name: Optional[str] = Field(None, description="User's full name")
    roles: list[str] = Field(
        default_factory=list, description="Assigned authorization roles"
    )
    is_active: bool = Field(True, description="Indicates if the user account is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FileMetadata(DomainModel):
    """Domain model representing metadata of an uploaded file stored in GCS."""

    id: str = Field(..., description="Unique UUID for the uploaded file")
    filename: str = Field(..., description="Original name of the file")
    content_type: str = Field(..., description="MIME content type of the file")
    size_bytes: int = Field(..., description="File size in bytes")
    gcs_uri: str = Field(..., description="Google Cloud Storage URI (gs://bucket/path)")
    public_url: str = Field(..., description="HTTPS download URL of the blob")
    uploaded_by: str = Field(..., description="UID of the user who uploaded the file")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = Field(
        False, description="Flag indicating if the file has been parsed into BigQuery"
    )


class DecisionRule(DomainModel):
    """Domain model representing a business rule evaluated by the Decision Engine."""

    id: str = Field(..., description="Unique identifier for the decision rule")
    name: str = Field(..., description="Descriptive name of the rule")
    expression: str = Field(..., description="Evaluation syntax or conditions")
    action: str = Field(
        ..., description="The output action or label applied when rule passes"
    )
    priority: int = Field(
        default=1, description="Priority level of execution (lower executes first)"
    )
    is_active: bool = Field(True, description="Is the rule active")
    created_by: str = Field(..., description="UID of the authoring analyst/user")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SimulationScenario(DomainModel):
    """Domain model representing scenario parameters for what-if simulations."""

    id: str = Field(..., description="Unique identifier for the simulation scenario")
    name: str = Field(..., description="Descriptive name of the simulation")
    parameters: dict[str, Any] = Field(
        ..., description="Key-value mapping of model inputs/variables"
    )
    base_dataset_id: str = Field(
        ..., description="Reference to BigQuery table/dataset used as base"
    )
    status: str = Field(
        "pending", description="Current status (pending, running, completed, failed)"
    )
    results_url: Optional[str] = Field(
        None, description="Path to simulation results output"
    )
    created_by: str = Field(..., description="UID of the user who initiated simulation")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnalyticsReport(DomainModel):
    """Domain model representing analytics reports exported from BigQuery."""

    id: str = Field(..., description="Unique identifier of the report")
    title: str = Field(..., description="Title of the report")
    query_executed: str = Field(
        ..., description="SQL query executed to build this report"
    )
    export_format: str = Field("csv", description="Format (csv, pdf, json)")
    gcs_uri: Optional[str] = Field(
        None, description="GCS URI location of exported file"
    )
    created_by: str = Field(..., description="UID of the creator")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PlatformNotification(DomainModel):
    """Domain model representing notifications dispatched to users."""

    id: str = Field(..., description="Unique identifier of the notification")
    recipient_id: str = Field(..., description="UID of the receiving user")
    title: str = Field(..., description="Brief title of the message")
    message: str = Field(..., description="Long message content")
    read: bool = Field(False, description="Has the recipient read the notification")
    created_at: datetime = Field(default_factory=datetime.utcnow)

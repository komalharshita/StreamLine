from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class SimulationCreate(BaseModel):
    """Payload to launch a new forecasting/scenario simulation."""

    name: str = Field(..., description="Descriptive title of the scenario")
    base_dataset_id: str = Field(
        ..., description="Identifier of the base BigQuery table to run against"
    )
    parameters: dict[str, Any] = Field(
        ...,
        description="Variables, overrides, and multiplier configurations for the run",
    )


class SimulationResponse(BaseModel):
    """Payload returned following a simulation query or execution."""

    id: str
    name: str
    base_dataset_id: str
    parameters: dict[str, Any]
    status: str = Field(
        ..., description="Current status: pending, running, completed, failed"
    )
    results_url: Optional[str] = None
    created_by: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    execution_time_seconds: Optional[float] = None

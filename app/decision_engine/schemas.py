from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class Decision(BaseModel):
    """Pydantic schema representing a generated Decision object."""

    decision_id: str = Field(..., description="Unique UUID for this generated decision")
    priority_score: float = Field(..., ge=0.0, le=100.0, description="Calculated priority score (0-100)")
    priority_level: str = Field(..., description="Qualitative priority tier: Critical, High, Medium, Low")
    category: str = Field(..., description="Type of detected issue (e.g., Revenue Drop, Inventory Shortage)")
    title: str = Field(..., description="Short user-friendly summary of the decision")
    description: str = Field(..., description="Detailed description of the findings")
    root_cause: str = Field(..., description="Inferred root cause for the issue")
    evidence: dict[str, Any] = Field(default_factory=dict, description="Key data metrics supporting the finding")
    financial_impact: float = Field(..., description="Projected financial impact in dollars")
    confidence_score: float = Field(..., ge=0.0, le=100.0, description="Inferred confidence level percentage")
    recommendation: str = Field(..., description="Deterministic actionable recommendation")
    expected_roi: float = Field(..., description="Expected Return on Investment percentage (e.g. 15.5%)")
    status: str = Field("active", description="Decision lifecycle state: active, dismissed, resolved")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

    class Config:
        from_attributes = True


class DecisionFeedResponse(BaseModel):
    """Payload representing the filtered feed returned to the client dashboard."""

    decisions: list[Decision]
    total_count: int
    critical_count: int
    high_count: int


class DecisionRefreshRequest(BaseModel):
    """Configuration to trigger a re-run of the detection engine over specific datasets."""

    workspace: Optional[str] = Field("default", description="Workspace context")
    override_thresholds: Optional[dict[str, float]] = Field(None, description="Optional custom limits")

from typing import Any
from pydantic import BaseModel, Field


class KPIMetric(BaseModel):
    """Schema representing an individual Key Performance Indicator metric."""

    key: str = Field(..., description="Unique slug for the metric")
    label: str = Field(..., description="Display title for the KPI card")
    value: float = Field(..., description="Current value of the KPI")
    change_percentage: float = Field(..., description="Percentage change compared to previous period")
    trend: str = Field("neutral", description="Trend direction: 'up', 'down', or 'neutral'")


class ChartSeries(BaseModel):
    """Schema representing an individual chart data series."""

    name: str = Field(..., description="Label for the data line/bar")
    data: list[float] = Field(..., description="Array of sequential values")


class AnalyticsDashboardResponse(BaseModel):
    """Response payload containing full aggregation of dashboard widgets."""

    kpi_cards: list[KPIMetric] = Field(default_factory=list)
    chart_labels: list[str] = Field(default_factory=list, description="X-axis timeline labels")
    chart_datasets: list[ChartSeries] = Field(default_factory=list)
    system_status: str = Field("operational", description="Status of analytical systems")

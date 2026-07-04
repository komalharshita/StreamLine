from typing import Any
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.dashboard import AnalyticsDashboardResponse, ChartSeries, KPIMetric

router = APIRouter()


@router.get("/metrics", response_model=AnalyticsDashboardResponse)
def get_dashboard_metrics(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> AnalyticsDashboardResponse:
    """Aggregates and returns core KPI metrics and chart datasets for visual dashboards.

    In production, this queries BigQuery aggregate tables to calculate metric scores.
    """
    # Simulated/Placeholder aggregates representing corporate metrics
    kpis = [
        KPIMetric(
            key="total_revenue",
            label="Total ARR",
            value=2450000.0,
            change_percentage=12.4,
            trend="up",
        ),
        KPIMetric(
            key="active_customers",
            label="Active Customers",
            value=1240.0,
            change_percentage=3.8,
            trend="up",
        ),
        KPIMetric(
            key="churn_rate",
            label="Gross Churn",
            value=0.021,
            change_percentage=-1.5,
            trend="down",
        ),
    ]

    chart_labels = ["Q1", "Q2", "Q3", "Q4"]
    chart_datasets = [
        ChartSeries(name="ARR growth", data=[500000.0, 1100000.0, 1800000.0, 2450000.0]),
        ChartSeries(name="Acquisitions cost", data=[45000.0, 52000.0, 48000.0, 60000.0]),
    ]

    return AnalyticsDashboardResponse(
        kpi_cards=kpis,
        chart_labels=chart_labels,
        chart_datasets=chart_datasets,
        system_status="operational",
    )

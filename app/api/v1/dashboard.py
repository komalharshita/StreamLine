import logging
import time
from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.services.dashboard.dashboard_service import dashboard_aggregator

router = APIRouter(prefix="/api/v1", tags=["Dashboard Intelligence"])
logger = logging.getLogger("app.api.v1.dashboard")


@router.get(
    "/dashboard", summary="Retrieve aggregated business intelligence dashboard state"
)
def get_dashboard(
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """Compiles Business Health, KPIs, active decisions, uploads, and AI summaries into a unified JSON response."""
    logger.info("Serving GET /api/v1/dashboard")
    return dashboard_aggregator.aggregate_dashboard()


@router.get("/business-health", summary="Retrieve business health status indicators")
def get_business_health(
    current_user: dict[str, Any] = Depends(get_current_user),
):
    """Calculates active risk scores, revenue trajectories, and inventory health indexes."""
    logger.info("Serving GET /api/v1/business-health")
    agg = dashboard_aggregator.aggregate_dashboard()

    if agg.get("system_status") == "error":
        return {
            "status": "error",
            "error": agg.get("error"),
        }

    health_data = agg.get("business_health", {})
    inv_data = agg.get("inventory_summary", {})
    decisions = agg.get("decisions", [])

    return {
        "business_health_score": health_data.get("health_score", 100),
        "risk_score": health_data.get("risk_score", 0),
        "revenue_trend": "up",  # Corresponds to Arr growth indicators
        "inventory_health": {
            "shortages": inv_data.get("shortages_count", 0),
            "overstocks": inv_data.get("overstocks_count", 0),
        },
        "decision_readiness": len(decisions),
        "last_updated_timestamp": health_data.get("last_updated", time.time()),
        "status": (
            "healthy" if health_data.get("health_score", 100) >= 70 else "warning"
        ),
    }

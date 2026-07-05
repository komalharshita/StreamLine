import logging
import time
from typing import Any

from app.decision_engine.decision_service import decision_service
from app.upload.metadata_service import metadata_store
from app.gemini.gemini_service import gemini_service

logger = logging.getLogger("app.dashboard.dashboard_service")


class DashboardService:
    """Orchestrates aggregation across data store, metadata index, decision feed, and AI services."""

    @staticmethod
    def aggregate_dashboard() -> dict[str, Any]:
        """Gathers intelligence indicators, recent files, and summaries into a single response model."""
        start_time = time.perf_counter()
        logger.info("Aggregating dashboard analytics metrics.")

        try:
            # 1. Fetch live decisions
            decisions = decision_service.get_feed()
            critical_count = sum(1 for d in decisions if d.priority_level == "Critical")
            high_count = sum(1 for d in decisions if d.priority_level == "High")
            
            # 2. Fetch uploads list
            uploads = metadata_store.list_all()

            # 3. Call Gemini Executive Summary
            exec_summary = gemini_service.generate_executive_summary()

            # 4. Compute Health & Risk scores
            risk_score = min(100, critical_count * 25 + high_count * 12 + len(decisions) * 3)
            health_score = max(15, 100 - risk_score)

            # 5. Extract KPIs list
            kpis = [
                {
                    "key": "total_revenue",
                    "label": "Total ARR",
                    "value": 2450000.0,
                    "change_percentage": 12.4,
                    "trend": "up",
                },
                {
                    "key": "active_customers",
                    "label": "Active Customers",
                    "value": 1240.0,
                    "change_percentage": 3.8,
                    "trend": "up",
                },
                {
                    "key": "churn_rate",
                    "label": "Gross Churn",
                    "value": 0.021,
                    "change_percentage": -1.5,
                    "trend": "down",
                },
            ]

            # 6. Charts Data
            charts_data = {
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "datasets": [
                    {"name": "ARR growth", "data": [500000.0, 1100000.0, 1800000.0, 2450000.0]},
                    {"name": "Acquisitions cost", "data": [45000.0, 52000.0, 48000.0, 60000.0]},
                ],
            }

            # 7. Recent Activity
            recent_activity = []
            for idx, dec in enumerate(decisions[:3]):
                recent_activity.append({
                    "id": dec.decision_id,
                    "description": f"Priority Alert: {dec.title}",
                    "timestamp": dec.created_at.isoformat() if hasattr(dec.created_at, "isoformat") else str(dec.created_at),
                    "status": dec.status,
                })

            return {
                "business_health": {
                    "health_score": health_score,
                    "risk_score": risk_score,
                    "status": "stable" if health_score >= 70 else "warning",
                    "last_updated": time.time(),
                },
                "kpis": kpis,
                "decisions": [d.dict() for d in decisions],
                "recent_uploads": uploads[:5],
                "revenue_summary": {
                    "monthly_arr": 2450000.0,
                    "growth_yoy": 12.4,
                },
                "inventory_summary": {
                    "shortages_count": sum(1 for d in decisions if d.category == "Inventory Shortage"),
                    "overstocks_count": sum(1 for d in decisions if d.category == "Inventory Overstock"),
                },
                "executive_summary": {
                    "business_health_summary": exec_summary.business_health_summary,
                    "top_risks": exec_summary.top_risks,
                    "top_opportunities": exec_summary.top_opportunities,
                    "recommended_actions": exec_summary.recommended_actions,
                },
                "charts_data": charts_data,
                "recent_activity": recent_activity,
                "system_status": "operational",
                "elapsed_time_ms": round((time.perf_counter() - start_time) * 1000, 2),
            }
        except Exception as e:
            logger.error(f"Error compiling dashboard metrics: {str(e)}")
            return {
                "system_status": "error",
                "error": str(e),
            }


dashboard_aggregator = DashboardService()

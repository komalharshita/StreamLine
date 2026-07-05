import logging
import threading
from typing import Optional

import pandas as pd
from fastapi import HTTPException, status

from app.decision_engine.decision_detector import DecisionDetector
from app.decision_engine.schemas import Decision

logger = logging.getLogger("app.decision_engine.decision_service")


class DecisionService:
    """Manages Decision Feed operations, filtering, and storage mapping."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._feed: dict[str, Decision] = {}

        # Seed default mock decisions for demo purposes
        from datetime import datetime

        mock_decisions = [
            Decision(
                decision_id="mock-dec-1",
                priority_score=88.5,
                priority_level="Critical",
                category="Inventory Shortage",
                title="Active Stockout Risk for Premium Smartwatches",
                description="Supply-chain delay in Singapore hub has caused premium smartwatch inventory to deplete to 3 days of safety stock. Demand projection forecasts a complete stockout within 48 hours.",
                root_cause="Singapore shipping container delays and unseasonal promotional demand surge.",
                evidence={"current_stock": 14, "forecast_demand_30d": 450, "safety_stock_limit": 50},
                financial_impact=18500.0,
                confidence_score=94.0,
                recommendation="Re-route 150 units from Tokyo satellite warehouse via expedited air freight to prevent imminent stockout.",
                expected_roi=42.0,
                status="active",
                created_at=datetime.utcnow()
            ),
            Decision(
                decision_id="mock-dec-2",
                priority_score=72.0,
                priority_level="High",
                category="Revenue Drop",
                title="Enterprise SaaS Plan Customer Churn Risk",
                description="Telemetry indicates that 3 major enterprise clients on the Premium Tier have ceased query activity by 75% week-over-week, indicating high probability of contract non-renewal.",
                root_cause="Customer support ticket backlog and product UI latency complaints.",
                evidence={"active_usage_drop": 75.0, "mrr_value": 4500.0},
                financial_impact=54000.0,
                confidence_score=85.0,
                recommendation="Assign Customer Success Director to contact accounts directly, issue API latency SLA credits, and prioritize query optimizations.",
                expected_roi=65.0,
                status="active",
                created_at=datetime.utcnow()
            ),
            Decision(
                decision_id="mock-dec-3",
                priority_score=45.5,
                priority_level="Medium",
                category="Inventory Overstock",
                title="Excess Warehouse Accumulation of Wireless Earbuds",
                description="Earbud stocks in Northern Virginia fulfillment center exceed standard storage velocity limits by 3.4x, leading to holding costs that deplete product margins.",
                root_cause="Over-ordering based on obsolete Q4 marketing projections.",
                evidence={"excess_stock": 2400, "monthly_velocity": 320},
                financial_impact=8200.0,
                confidence_score=78.5,
                recommendation="Deploy a targeted 15% markdown campaign or group items into holiday bundles to accelerate storage velocity.",
                expected_roi=18.0,
                status="active",
                created_at=datetime.utcnow()
            )
        ]
        for d in mock_decisions:
            self._feed[d.decision_id] = d

    def get_feed(
        self,
        category: Optional[str] = None,
        priority_level: Optional[str] = None,
        status_filter: Optional[str] = "active",
    ) -> list[Decision]:
        """Returns lists of generated Decisions, applying optional filters."""
        with self._lock:
            results = list(self._feed.values())

        if category:
            results = [d for d in results if d.category.lower() == category.lower()]
        if priority_level:
            results = [
                d for d in results if d.priority_level.lower() == priority_level.lower()
            ]
        if status_filter:
            results = [d for d in results if d.status.lower() == status_filter.lower()]

        # Sort decisions by Priority Score descending
        results.sort(key=lambda x: x.priority_score, reverse=True)
        return results

    def get_decision(self, decision_id: str) -> Decision:
        """Retrieves a single Decision by its unique UUID.

        Raises HTTPException 404 if not found.
        """
        with self._lock:
            decision = self._feed.get(decision_id)

        if not decision:
            logger.warning(f"Decision retrieval failed: ID '{decision_id}' not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Decision with ID '{decision_id}' not found.",
            )
        return decision

    def refresh_feed_from_dataframe(
        self, df: pd.DataFrame, dataset_type: str
    ) -> list[Decision]:
        """Evaluates a DataFrame against rules based on dataset_type and saves results to the feed."""
        logger.info(f"Triggering decision feed refresh for type: '{dataset_type}'")

        detected_decisions = []
        dtype = (dataset_type or "").lower().strip()

        if "sale" in dtype:
            detected_decisions = DecisionDetector.detect_sales_decisions(df)
        elif "invent" in dtype:
            detected_decisions = DecisionDetector.detect_inventory_decisions(df)
        elif "transact" in dtype or "finance" in dtype:
            detected_decisions = DecisionDetector.detect_financial_decisions(df)
        else:
            # Run generic detection across matches if layout fits
            detected_decisions = DecisionDetector.detect_sales_decisions(
                df
            ) + DecisionDetector.detect_inventory_decisions(df)

        # Merge into the in-memory feed repository
        with self._lock:
            for decision in detected_decisions:
                self._feed[decision.decision_id] = decision

        logger.info(
            f"Feed refreshed. Generated {len(detected_decisions)} new decisions."
        )
        return detected_decisions

    def update_decision_status(self, decision_id: str, new_status: str) -> Decision:
        """Updates decision status (e.g., 'dismissed', 'resolved')."""
        with self._lock:
            if decision_id not in self._feed:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Decision with ID '{decision_id}' not found.",
                )
            self._feed[decision_id].status = new_status
            return self._feed[decision_id]


# Singleton service instance
decision_service = DecisionService()

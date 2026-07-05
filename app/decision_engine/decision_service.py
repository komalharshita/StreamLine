import logging
import threading
from typing import Optional
import pandas as pd
from fastapi import HTTPException, status

from app.decision_engine.schemas import Decision
from app.decision_engine.decision_detector import DecisionDetector

logger = logging.getLogger("app.decision_engine.decision_service")


class DecisionService:
    """Manages Decision Feed operations, filtering, and storage mapping."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._feed: dict[str, Decision] = {}

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
            results = [d for d in results if d.priority_level.lower() == priority_level.lower()]
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
            detected_decisions = (
                DecisionDetector.detect_sales_decisions(df)
                + DecisionDetector.detect_inventory_decisions(df)
            )

        # Merge into the in-memory feed repository
        with self._lock:
            for decision in detected_decisions:
                self._feed[decision.decision_id] = decision

        logger.info(f"Feed refreshed. Generated {len(detected_decisions)} new decisions.")
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

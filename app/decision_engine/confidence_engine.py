import logging
from app.decision_engine.utils import clamp

logger = logging.getLogger("app.decision_engine.confidence_engine")


class ConfidenceEngine:
    """Calculates decision confidence percentage based on data completeness, freshness, and rule integrity."""

    @staticmethod
    def calculate_confidence(
        completeness: float = 100.0,
        consistency: float = 100.0,
        freshness: float = 100.0,
        rule_weight: float = 95.0,
    ) -> float:
        """Computes a composite confidence score percentage.

        Average of factors. Clamped between 0 and 100.
        """
        comp = clamp(completeness)
        cons = clamp(consistency)
        fresh = clamp(freshness)
        rule = clamp(rule_weight)

        confidence = (comp + cons + fresh + rule) / 4.0
        return round(clamp(confidence), 2)

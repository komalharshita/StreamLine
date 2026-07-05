import logging

from app.decision_engine.utils import clamp

logger = logging.getLogger("app.decision_engine.priority_engine")


class PriorityEngine:
    """Computes weighted Priority Scores (0-100) and maps them to qualitative levels."""

    @staticmethod
    def calculate_priority(
        financial_impact: float,
        urgency: float,
        confidence: float,
        criticality: float,
    ) -> tuple[float, str]:
        """Calculates Priority Score.

        Formula:
        Priority = (Financial Impact Score * 0.40) + (Urgency * 0.30) + (Confidence * 0.20) + (Criticality * 0.10)

        Returns (priority_score, priority_level).
        """
        # Normalize financial impact: assume $50,000 as base ceiling for 100/100 score
        financial_score = clamp((abs(financial_impact) / 50000.0) * 100.0)

        urg_score = clamp(urgency)
        conf_score = clamp(confidence)
        crit_score = clamp(criticality)

        # Weighted score summation
        priority_score = (
            (financial_score * 0.40)
            + (urg_score * 0.30)
            + (conf_score * 0.20)
            + (crit_score * 0.10)
        )
        priority_score = round(clamp(priority_score), 2)

        # Map to priority levels
        if priority_score >= 80.0:
            level = "Critical"
        elif priority_score >= 60.0:
            level = "High"
        elif priority_score >= 40.0:
            level = "Medium"
        else:
            level = "Low"

        logger.debug(f"Calculated priority score {priority_score} ({level})")
        return priority_score, level

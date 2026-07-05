import logging

logger = logging.getLogger("app.decision_engine.utils")


def clamp(val: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Clamps a floating point value between min and max bounds."""
    return max(min_val, min(max_val, float(val)))


def estimate_roi(financial_impact: float, implementation_cost: float) -> float:
    """Estimates the ROI percentage based on financial impact and cost.

    Example: impact $15,000, cost $5,000 -> 200.0%
    """
    if implementation_cost <= 0:
        return 0.0
    roi = ((financial_impact - implementation_cost) / implementation_cost) * 100.0
    return max(0.0, round(roi, 2))

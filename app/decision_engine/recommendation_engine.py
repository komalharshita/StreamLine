import logging
from typing import Any

logger = logging.getLogger("app.decision_engine.recommendation_engine")


class RecommendationEngine:
    """Generates deterministic actionable recommendations and estimates expected ROI outcomes."""

    @staticmethod
    def generate_recommendation_and_roi(
        category: str, evidence: dict[str, Any]
    ) -> tuple[str, float]:
        """Maps an issue category to standard business recommendations and expected ROI percentages.

        Returns (recommendation_string, expected_roi_percentage).
        """
        # Lowercase for safe matching
        cat = category.lower().strip()

        if "revenue drop" in cat:
            rec = "Deploy an targeted marketing campaign on top categories and limit active discount margins to protect base revenue."
            roi = 18.5
        elif "shortage" in cat:
            item = evidence.get("product_name", "affected SKUs")
            rec = f"Immediately submit replenishment order for {item} to satisfy incoming safety stock requirements."
            roi = 25.0
        elif "overstock" in cat:
            item = evidence.get("product_name", "excess products")
            rec = f"Initiate a flash sale promotion or bundle offer for {item} to free up warehouse space and working capital."
            roi = 12.0
        elif "churn" in cat:
            rec = "Trigger automated customer winback emails offering customized credit incentives for inactive accounts."
            roi = 35.5
        elif "slow moving" in cat:
            item = evidence.get("product_name", "static items")
            rec = f"Discontinue further orders of {item} and negotiate liquidating static floor items to recover capital."
            roi = 15.0
        elif "expense spike" in cat:
            category_name = evidence.get("expense_category", "affected accounts")
            rec = f"Audit expense growth in '{category_name}' category and initiate renegotiations on procurement supplier rates."
            roi = 22.0
        elif "pricing" in cat:
            item = evidence.get("product_name", "highly inelastic SKUs")
            rec = f"Test increasing product pricing margins by 5% on '{item}' to capture inelastic demand opportunities."
            roi = 40.0
        elif "high performing" in cat:
            item = evidence.get("product_name", "top items")
            rec = f"Increase active advertising budget allocation on '{item}' and place them in premium display zones."
            roi = 30.0
        else:
            rec = "Conduct deep-dive operational audit on category performance to identify efficiency improvement opportunities."
            roi = 10.0

        logger.debug(f"Generated recommendation for '{category}': {rec} (ROI: {roi}%)")
        return rec, roi

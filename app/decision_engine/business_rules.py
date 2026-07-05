from typing import Any

# Default thresholds parameterizing the business rules
DEFAULT_THRESHOLDS: dict[str, Any] = {
    "revenue_drop_percentage": 15.0,  # drop limit (> 15% period-over-period)
    "inventory_shortage_weeks": 2.0,  # stock coverage below 2 weeks
    "inventory_overstock_weeks": 8.0,  # stock coverage above 8 weeks
    "churn_inactive_days": 60,  # inactivity limit (> 60 days)
    "slow_moving_days": 30,  # product with 0 sales velocity for > 30 days
    "expense_spike_percentage": 20.0,  # expense over category average by > 20%
    "pricing_opportunity_elasticity": 0.5,  # inelastic demand threshold
}

import logging
import re
from typing import Any

logger = logging.getLogger("app.cleaning.utils")


def clean_currency_value(val: Any) -> float:
    """Helper to convert currency string format to float.

    Example: '$1,500.50' -> 1500.50
    """
    if val is None or (isinstance(val, float) and val != val):  # NaN check
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)

    # Remove symbols like $, €, £ and commas
    cleaned = re.sub(r"[^\d\.\-]", "", str(val))
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def clean_percentage_value(val: Any) -> float:
    """Helper to convert percentage string format to decimal float.

    Example: '12.5%' -> 0.125
    """
    if val is None or (isinstance(val, float) and val != val):  # NaN check
        return 0.0
    if isinstance(val, (int, float)):
        # If float/int, check if it's already decimal or needs scale
        # For percentages, if user uploads numeric '12.5', they mean 0.125
        # We assume text formatted percentages require division by 100
        return float(val)

    cleaned = re.sub(r"[^\d\.\-]", "", str(val))
    try:
        return float(cleaned) / 100.0 if cleaned else 0.0
    except ValueError:
        return 0.0


def clean_text_trim(val: Any) -> str:
    """Safely converts value to string and strips spaces."""
    if val is None or (isinstance(val, float) and val != val):
        return ""
    return str(val).strip()

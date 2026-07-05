import logging
from fastapi import HTTPException, status
import pandas as pd

logger = logging.getLogger("app.cleaning.validators")

SUPPORTED_DATASETS = {"Sales", "Inventory", "Financial Transactions"}


class CleaningValidator:
    """Enforces structure, dimensions, and type validations on uploaded datasets."""

    @staticmethod
    def validate_dataframe(df: pd.DataFrame, dataset_type: str = None) -> None:
        """Validates basic dataframe integrity and dimension bounds.

        Raises HTTPException if validation checks fail.
        """
        logger.info("Running dataframe structure validation check.")

        # 1. Check if empty
        if df.empty:
            logger.warning("Cleaning Validation Failed: DataFrame is empty.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset validation failed: The dataset contains no records or data rows.",
            )

        # 2. Check column count
        if len(df.columns) == 0:
            logger.warning("Cleaning Validation Failed: DataFrame contains zero columns.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset validation failed: The dataset contains no valid column headers.",
            )

        # 3. Verify dataset category template if provided
        if dataset_type and dataset_type not in SUPPORTED_DATASETS:
            logger.warning(f"Cleaning Validation Failed: Unsupported dataset type '{dataset_type}'.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Dataset validation failed: Dataset template '{dataset_type}' is not supported. "
                    f"Supported templates are: {', '.join(SUPPORTED_DATASETS)}."
                ),
            )

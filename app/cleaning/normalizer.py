import logging
import re
from typing import Any, Mapping
import pandas as pd

from app.cleaning.utils import (
    clean_currency_value,
    clean_percentage_value,
    clean_text_trim,
)

logger = logging.getLogger("app.cleaning.normalizer")


class DataNormalizer:
    """Operations layer standardizing structures and imputing data fields inside DataFrames."""

    @staticmethod
    def sanitize_column_names(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
        """Converts all column headers to snake_case, lowercases, removes special characters, and trims spaces.

        Returns (cleaned_dataframe, mapping_dictionary).
        """
        logger.info("Normalizing column headers.")
        renamed_map = {}
        cleaned_columns = []

        for col in df.columns:
            orig = str(col)
            # Lowercase
            val = orig.lower().strip()
            # Replace non-alphanumeric chars with underscores
            val = re.sub(r"[^\w]", "_", val)
            # Remove leading numbers check
            if val and val[0].isdigit():
                val = f"_{val}"
            # Deduplicate underscores and strip
            val = re.sub(r"_+", "_", val).strip("_")
            val = val or f"column_{len(cleaned_columns)}"

            renamed_map[orig] = val
            cleaned_columns.append(val)

        df_copy = df.copy()
        df_copy.columns = cleaned_columns
        return df_copy, renamed_map

    @staticmethod
    def normalize_value_formats(
        df: pd.DataFrame, inferred_types: dict[str, str]
    ) -> tuple[pd.DataFrame, int]:
        """Normalizes Currency text fields to float representation and Percentage text fields to decimal scale floats.

        Returns (dataframe, count_of_cells_normalized).
        """
        logger.info("Normalizing currency and percentage fields.")
        df_copy = df.copy()
        normalized_count = 0

        for col in df_copy.columns:
            col_type = inferred_types.get(col)
            if col_type == "Currency":
                # Detect cells filled before conversion
                nulls_before = df_copy[col].isna().sum()
                df_copy[col] = df_copy[col].apply(clean_currency_value)
                # Count non-null conversions as modifications
                normalized_count += len(df_copy) - nulls_before
            elif col_type == "Percentage":
                nulls_before = df_copy[col].isna().sum()
                df_copy[col] = df_copy[col].apply(clean_percentage_value)
                normalized_count += len(df_copy) - nulls_before

        return df_copy, int(normalized_count)

    @staticmethod
    def handle_missing_values(
        df: pd.DataFrame, inferred_types: dict[str, str]
    ) -> tuple[pd.DataFrame, int]:
        """Resolves missing cells using strategic imputations based on custom datatype categories.

        Numeric (Integer, Float, Currency, Percentage) -> Median
        Categorical (Category, Text) -> Mode
        Datetime -> Forward Fill
        Boolean -> False
        """
        logger.info("Executing missing values resolution.")
        df_copy = df.copy()
        total_filled = 0

        for col in df_copy.columns:
            missing_mask = df_copy[col].isna()
            missing_count = int(missing_mask.sum())
            if missing_count == 0:
                continue

            col_type = inferred_types.get(col)
            
            # Numeric strategy: Median
            if col_type in {"Integer", "Float", "Currency", "Percentage"}:
                # If all are missing, default to 0.0
                median_val = df_copy[col].median()
                if pd.isna(median_val):
                    median_val = 0.0
                df_copy[col] = df_copy[col].fillna(median_val)
                
            # Categorical strategy: Mode
            elif col_type in {"Category", "Text"}:
                mode_series = df_copy[col].mode()
                mode_val = mode_series.iloc[0] if not mode_series.empty else "Unknown"
                df_copy[col] = df_copy[col].fillna(mode_val)

            # Datetime strategy: Forward Fill (with backward fill fallback if first rows are empty)
            elif col_type == "Datetime":
                # Ensure date datatype is active before filling
                df_copy[col] = pd.to_datetime(df_copy[col], errors="coerce")
                df_copy[col] = df_copy[col].ffill().bfill()
                # If still null (e.g. all empty date columns), default to today
                if df_copy[col].isna().any():
                    df_copy[col] = df_copy[col].fillna(pd.Timestamp.utcnow())

            # Boolean strategy: False
            elif col_type == "Boolean":
                df_copy[col] = df_copy[col].fillna(False)

            total_filled += missing_count

        return df_copy, int(total_filled)

    @staticmethod
    def parse_dates(df: pd.DataFrame, inferred_types: dict[str, str]) -> pd.DataFrame:
        """Coerces columns classified as Datetime into actual Pandas Timestamp types."""
        logger.info("Coercing Datetime formatting.")
        df_copy = df.copy()
        for col in df_copy.columns:
            if inferred_types.get(col) == "Datetime":
                df_copy[col] = pd.to_datetime(df_copy[col], errors="coerce")
        return df_copy

    @staticmethod
    def trim_whitespace(df: pd.DataFrame, inferred_types: dict[str, str]) -> pd.DataFrame:
        """Trims leading/trailing spaces from string fields (Category and Text)."""
        logger.info("Trimming whitespaces from text columns.")
        df_copy = df.copy()
        for col in df_copy.columns:
            if inferred_types.get(col) in {"Category", "Text"}:
                df_copy[col] = df_copy[col].apply(clean_text_trim)
        return df_copy

    @staticmethod
    def remove_completely_empty_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
        """Eliminates rows that contain exclusively null or blank values.

        Returns (cleaned_dataframe, count_of_removed_rows).
        """
        logger.info("Scanning for completely empty rows.")
        initial_len = len(df)
        
        # Drops rows where all cells are NA
        cleaned_df = df.dropna(how="all")
        removed_count = initial_len - len(cleaned_df)
        
        return cleaned_df, int(removed_count)

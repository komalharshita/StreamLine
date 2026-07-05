import logging
import re
from typing import Any
import pandas as pd

logger = logging.getLogger("app.cleaning.data_profiler")


class DataProfiler:
    """Performs datatype inference, schema profiling, and structures audit metadata."""

    @staticmethod
    def infer_column_type(series: pd.Series) -> str:
        """Infers the custom logical datatype of a column series."""
        # Drop missing values for type inference
        non_null_series = series.dropna()
        if non_null_series.empty:
            return "Text"

        dtype = series.dtype

        # 1. Direct system matches
        if pd.api.types.is_integer_dtype(dtype):
            return "Integer"
        if pd.api.types.is_float_dtype(dtype):
            return "Float"
        if pd.api.types.is_bool_dtype(dtype):
            return "Boolean"
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return "Datetime"

        # Check sample representation to avoid scanning millions of rows
        sample = non_null_series.head(500).astype(str).str.strip()

        # 2. Check boolean text mapping representation
        bool_words = {"true", "false", "yes", "no", "1", "0", "1.0", "0.0"}
        if all(val.lower() in bool_words for val in sample):
            return "Boolean"

        # 3. Check percentage format
        pct_pattern = re.compile(r"^[-+]?\d*\.?\d+\s*%$")
        if all(pct_pattern.match(val) for val in sample):
            return "Percentage"

        # 4. Check currency format
        currency_pattern = re.compile(r"^[\$\u20ac\u00a3\u00a5]?\s*[-+]?[\d,]*\.?\d+\s*$")
        if any(val.startswith(("$", "€", "£", "¥")) for val in sample) and all(
            currency_pattern.match(val) for val in sample
        ):
            return "Currency"

        # 5. Check datetime string parsing
        try:
            # Check if all can parse to dates using pandas datetime parser
            pd.to_datetime(sample, errors="raise")
            return "Datetime"
        except (ValueError, TypeError, OverflowError):
            pass

        # 6. Check Category vs Text based on cardinality ratio
        num_unique = non_null_series.nunique()
        total_count = len(non_null_series)
        cardinality_ratio = num_unique / total_count if total_count > 0 else 1.0

        if num_unique < 50 and cardinality_ratio < 0.20:
            return "Category"

        return "Text"

    @classmethod
    def profile_dataframe(cls, df: pd.DataFrame) -> dict[str, Any]:
        """Profiles the dataset to discover datatypes, missing cell distributions, and cardinality maps."""
        logger.info("Profiling dataframe columns.")
        profile = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_counts": {},
            "data_types": {},
        }

        for col in df.columns:
            # Inferred logical types
            inferred_type = cls.infer_column_type(df[col])
            profile["data_types"][str(col)] = inferred_type
            
            # Missing value counts
            missing_count = int(df[col].isna().sum())
            profile["missing_counts"][str(col)] = missing_count

        return profile

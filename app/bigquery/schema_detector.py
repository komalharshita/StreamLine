import logging
import re

import pandas as pd
from google.cloud import bigquery

from app.bigquery.exceptions import SchemaDetectionError

logger = logging.getLogger("app.bigquery.schema_detector")


class SchemaDetector:
    """Helper to detect BigQuery schemas from Pandas DataFrames and sanitize column names."""

    @staticmethod
    def sanitize_column_name(name: str) -> str:
        """Sanitizes a column name to conform to BigQuery constraints.

        Only alphanumeric characters and underscores are allowed.
        """
        # Replace non-alphanumeric/underscore characters with underscores
        sanitized = re.sub(r"[^\w]", "_", name)
        # Ensure it doesn't start with a number (prepend an underscore if so)
        if sanitized and sanitized[0].isdigit():
            sanitized = f"_{sanitized}"
        # Strip trailing/leading underscores
        sanitized = sanitized.strip("_")
        return sanitized or "column"

    @classmethod
    def detect_schema(cls, df: pd.DataFrame) -> list[bigquery.SchemaField]:
        """Inspects Pandas DataFrame column types and constructs BigQuery SchemaFields.

        Raises SchemaDetectionError if detection fails.
        """
        logger.debug("Detecting schema fields from DataFrame.")
        if df.columns.empty:
            raise SchemaDetectionError(
                "Cannot detect schema for an empty DataFrame (no columns)."
            )

        schema_fields = []
        for col in df.columns:
            col_name = str(col)
            sanitized_name = cls.sanitize_column_name(col_name)
            dtype = df[col].dtype

            # Map pandas datatypes to BigQuery types
            if pd.api.types.is_integer_dtype(dtype):
                field_type = "INTEGER"
            elif pd.api.types.is_float_dtype(dtype):
                field_type = "FLOAT"
            elif pd.api.types.is_bool_dtype(dtype):
                field_type = "BOOLEAN"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                field_type = "TIMESTAMP"
            else:
                # Default fallback for objects, categories, strings
                field_type = "STRING"

            logger.debug(
                f"Mapped column '{col_name}' -> '{sanitized_name}' ({dtype}) to BigQuery type: '{field_type}'"
            )
            schema_fields.append(
                bigquery.SchemaField(
                    name=sanitized_name, field_type=field_type, mode="NULLABLE"
                )
            )

        return schema_fields

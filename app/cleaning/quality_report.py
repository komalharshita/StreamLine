import logging
import time
from typing import Any
import pandas as pd

from app.cleaning.schemas import DataQualityReport

logger = logging.getLogger("app.cleaning.quality_report")


class QualityReporter:
    """Calculates dataset quality scores (0-100) and collects anomaly warnings."""

    @staticmethod
    def calculate_score_and_report(
        initial_df: pd.DataFrame,
        cleaned_df: pd.DataFrame,
        missing_filled: int,
        duplicates_removed: int,
        empty_rows_removed: int,
        renamed_columns: dict[str, str],
        data_types: dict[str, str],
        start_time: float,
    ) -> DataQualityReport:
        """Calculates indicators, compiles warnings, and computes the 0-100 quality score."""
        logger.info("Compiling Data Quality Report metrics.")

        total_cells = initial_df.size
        missing_percentage = (missing_filled / total_cells) if total_cells > 0 else 0.0
        duplicate_percentage = (duplicates_removed / len(initial_df)) if len(initial_df) > 0 else 0.0

        # Quality score formula (starts at 100, drops on missing/duplicate density)
        # 1. Missing cells deduct up to 50 points
        missing_deduction = missing_percentage * 50.0
        # 2. Duplicates deduct up to 30 points
        duplicate_deduction = duplicate_percentage * 30.0
        # 3. Completely empty rows deduct up to 10 points
        empty_deduction = (empty_rows_removed / len(initial_df) * 10.0) if len(initial_df) > 0 else 0.0

        score = max(0.0, min(100.0, 100.0 - missing_deduction - duplicate_deduction - empty_deduction))

        # Compile warnings
        warnings = []
        if duplicates_removed > 0:
            warnings.append(f"Identified and eliminated {duplicates_removed} duplicate row records.")
        if missing_filled > 0:
            warnings.append(
                f"Imputed {missing_filled} missing values (Missing Density: {missing_percentage:.2%})."
            )
        if empty_rows_removed > 0:
            warnings.append(f"Cleaned {empty_rows_removed} completely blank rows from the source sheet.")
        if renamed_columns:
            warnings.append(f"Standardized {len(renamed_columns)} headers into snake_case format.")
        
        # Low quality warnings
        if score < 70.0:
            warnings.append(f"Warning: Low dataset quality score: {score:.1f}/100. Inspect source structure.")

        errors = []
        # If score drops to 0, or dimensions are corrupted
        if cleaned_df.empty:
            errors.append("Critical Error: Cleaning resulted in an empty DataFrame.")

        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 3)

        return DataQualityReport(
            total_rows=len(initial_df) + empty_rows_removed,
            total_columns=len(initial_df.columns),
            rows_removed=empty_rows_removed,
            duplicates_removed=duplicates_removed,
            missing_values_filled=missing_filled,
            columns_renamed=renamed_columns,
            detected_data_types=data_types,
            quality_score=round(score, 2),
            warnings=warnings,
            errors=errors,
            processing_time_ms=processing_time_ms,
        )

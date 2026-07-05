import logging
import time
from typing import Optional

import pandas as pd

from app.cleaning.data_profiler import DataProfiler
from app.cleaning.normalizer import DataNormalizer
from app.cleaning.quality_report import QualityReporter
from app.cleaning.schemas import CleaningConfig, DataQualityReport
from app.cleaning.validators import CleaningValidator

logger = logging.getLogger("app.cleaning.cleaning_service")


class DataCleaningService:
    """Master service class coordinating the data cleaning and preprocessing pipeline steps."""

    @staticmethod
    def clean_dataset(
        df: pd.DataFrame, config: Optional[CleaningConfig] = None
    ) -> tuple[pd.DataFrame, DataQualityReport]:
        """Validates, profiles, standardizes formats, resolves missing data, and generates a Quality Report.

        Returns (cleaned_dataframe, data_quality_report).
        """
        start_time = time.perf_counter()
        config = config or CleaningConfig()
        logger.info(
            f"Starting dataset cleaning pipeline. Template: {config.dataset_type or 'Generic'}"
        )

        # 1. Structural Checks & Validation
        CleaningValidator.validate_dataframe(df, config.dataset_type)

        # Preserve the initial state for quality diffs
        initial_df = df.copy()

        # Step 2: Remove completely empty rows first
        df_cleaned, empty_rows_removed = DataNormalizer.remove_completely_empty_rows(df)

        # Step 3: Standardize column names
        df_cleaned, renamed_columns = DataNormalizer.sanitize_column_names(df_cleaned)

        # Step 4: Profile and Infer data types
        profile = DataProfiler.profile_dataframe(df_cleaned)
        inferred_types = profile["data_types"]

        # Step 5: Normalize currencies and percentages
        if config.normalize_currencies or config.normalize_percentages:
            df_cleaned, _ = DataNormalizer.normalize_value_formats(
                df_cleaned, inferred_types
            )

        # Step 6: Handle missing values (imputation)
        missing_filled = 0
        if config.impute_missing:
            df_cleaned, missing_filled = DataNormalizer.handle_missing_values(
                df_cleaned, inferred_types
            )

        # Step 7: Parse dates coercion
        df_cleaned = DataNormalizer.parse_dates(df_cleaned, inferred_types)

        # Step 8: Trim text fields whitespace
        df_cleaned = DataNormalizer.trim_whitespace(df_cleaned, inferred_types)

        # Step 9: Drop duplicates
        duplicates_removed = 0
        if config.remove_duplicates:
            initial_rows = len(df_cleaned)
            df_cleaned = df_cleaned.drop_duplicates()
            duplicates_removed = initial_rows - len(df_cleaned)

        # 10. Generate data quality report
        report = QualityReporter.calculate_score_and_report(
            initial_df=initial_df,
            cleaned_df=df_cleaned,
            missing_filled=missing_filled,
            duplicates_removed=duplicates_removed,
            empty_rows_removed=empty_rows_removed,
            renamed_columns=renamed_columns,
            data_types=inferred_types,
            start_time=start_time,
        )

        logger.info(
            f"Finished dataset cleaning pipeline. Score: {report.quality_score}/100. Duration: {report.processing_time_ms}ms"
        )
        return df_cleaned, report


# Singleton service instance
cleaning_service = DataCleaningService()

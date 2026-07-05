from typing import Any, Optional
from pydantic import BaseModel, Field


class DataQualityReport(BaseModel):
    """Pydantic schema representing the generated Data Quality Report."""

    total_rows: int = Field(..., description="Initial total rows in the dataset")
    total_columns: int = Field(..., description="Initial total columns in the dataset")
    rows_removed: int = Field(..., description="Count of completely empty rows removed")
    duplicates_removed: int = Field(..., description="Count of duplicate rows removed")
    missing_values_filled: int = Field(..., description="Total count of missing data cells imputed")
    columns_renamed: dict[str, str] = Field(
        default_factory=dict, description="Mapping of original column names to sanitized snake_case columns"
    )
    detected_data_types: dict[str, str] = Field(
        default_factory=dict, description="Inferred datatype categories mapped per column"
    )
    quality_score: float = Field(..., ge=0.0, le=100.0, description="Overall computed quality score (0-100)")
    warnings: list[str] = Field(default_factory=list, description="Non-blocking warning messages about data anomalies")
    errors: list[str] = Field(default_factory=list, description="Blocking validation errors identified during processing")
    processing_time_ms: float = Field(..., description="Total cleaning pipeline processing duration in milliseconds")


class CleaningConfig(BaseModel):
    """Configuration options parameterizing the data cleaning pipeline."""

    dataset_type: Optional[str] = Field(
        None, description="Type of business dataset: 'Sales', 'Inventory', or 'Financial Transactions'"
    )
    impute_missing: bool = Field(True, description="Enable automatic missing value imputation")
    remove_duplicates: bool = Field(True, description="Enable duplicate row elimination")
    normalize_currencies: bool = Field(True, description="Enable currency text to float normalization")
    normalize_percentages: bool = Field(True, description="Enable percentage text to decimal float normalization")

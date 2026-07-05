import logging

import pandas as pd

logger = logging.getLogger("app.upload.analyzer")


class DatasetAnalyzer:
    """Intelligent schema-based dataset type detection and deep quality report audits."""

    @staticmethod
    def infer_dataset_type(columns: list[str]) -> tuple[str, float]:
        """Infers the dataset type (Sales, Inventory, HR, Finance, Marketing) based on column presence scoring."""
        col_set = {str(c).lower().strip() for c in columns}

        rules = {
            "Sales": [
                "order_id",
                "customer_id",
                "amount",
                "order_date",
                "sale",
                "price",
                "revenue",
                "cost",
                "customer",
                "client",
                "product_id",
            ],
            "Inventory": [
                "sku",
                "warehouse",
                "stock",
                "quantity",
                "item",
                "product",
                "location",
                "bin",
                "on_hand",
                "reorder",
            ],
            "HR": [
                "employee",
                "department",
                "salary",
                "staff",
                "wage",
                "role",
                "manager",
                "hire_date",
                "position",
            ],
            "Finance": [
                "transaction",
                "account",
                "balance",
                "credit",
                "debit",
                "ledger",
                "asset",
                "liability",
                "equity",
            ],
            "Marketing": [
                "campaign",
                "clicks",
                "impressions",
                "ad",
                "views",
                "ctr",
                "spend",
                "conversions",
                "leads",
            ],
        }

        scores = {}
        for dtype, keywords in rules.items():
            score = 0
            for kw in keywords:
                for col in col_set:
                    if kw in col or col in kw:
                        score += 2
                        if col == kw:
                            score += 3
            scores[dtype] = score

        best_type = max(scores, key=scores.get)
        max_score = scores[best_type]

        if max_score == 0:
            logger.info("No matching schema rules found. Defaulting to Sales dataset type.")
            return "Sales", 0.50

        # Compute confidence percentage (bounded between 50% and 99%)
        confidence = min(0.99, 0.5 + (max_score / (len(columns) * 2 + 1)))
        logger.info(f"Dataset type inferred: '{best_type}' with confidence: {confidence:.2%}")
        return best_type, confidence

    @staticmethod
    def generate_quality_report(df: pd.DataFrame) -> dict:
        """Runs validation checks to build a Quality Score, warnings list, and action recommendations."""
        warnings = []
        recommendations = []

        total_rows = len(df)
        total_cols = len(df.columns)
        if total_rows == 0:
            return {
                "quality_score": 10,
                "warnings": ["The uploaded dataset is empty (has 0 rows)."],
                "recommendations": ["Ensure you upload a non-empty CSV/Excel file."],
            }

        deduction = 0

        # 1. Duplicate Column Names
        col_names = [str(c) for c in df.columns]
        if total_cols != len(set(col_names)):
            warnings.append("Duplicate column headers detected.")
            recommendations.append("Ensure each column name in the header row is unique.")
            deduction += 10

        # 2. Empty Column Names
        empty_cols = [
            c for c in col_names if c.strip() == "" or c.startswith("Unnamed:")
        ]
        if empty_cols:
            warnings.append(f"{len(empty_cols)} empty column header labels detected.")
            recommendations.append("Provide descriptive header names for all columns.")
            deduction += len(empty_cols) * 4

        # 3. Entirely Empty Columns
        all_null_cols = [
            str(c) for c in df.columns if df[c].isnull().all()
        ]
        if all_null_cols:
            warnings.append(
                f"Entirely empty columns: {', '.join(all_null_cols[:4])}"
                + ("..." if len(all_null_cols) > 4 else "")
            )
            recommendations.append("Remove empty columns that contain zero data values.")
            deduction += len(all_null_cols) * 5

        # 4. Duplicate Rows
        dup_rows = int(df.duplicated().sum())
        if dup_rows > 0:
            pct_dup = (dup_rows / total_rows) * 100
            warnings.append(f"{dup_rows} duplicate rows detected ({pct_dup:.1f}%).")
            recommendations.append("Remove duplicate records to prevent skewed analysis.")
            deduction += min(15, int(pct_dup * 1.5))

        # 5. Missing Values Check
        has_missing = False
        for col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                pct = (null_count / total_rows) * 100
                if pct > 5.0:
                    warnings.append(
                        f"Column '{col}' has {pct:.1f}% missing values."
                    )
                    deduction += min(8, int(pct * 0.4))
                has_missing = True
        if has_missing:
            recommendations.append("Fill or impute missing cells using statistical averages.")

        # 6. Mixed Datatypes / Numeric Parsing Issues
        for col in df.columns:
            if df[col].dtype == "object":
                # Check if it fails numeric parse but looks mostly numeric
                try:
                    parsed = pd.to_numeric(df[col], errors="coerce")
                    non_numeric = parsed.isnull().sum() - df[col].isnull().sum()
                    if 0 < non_numeric < total_rows * 0.5:
                        warnings.append(
                            f"Column '{col}' contains mixed text and numeric values."
                        )
                        recommendations.append(
                            f"Clean non-numeric characters (currency signs, symbols) from '{col}'."
                        )
                        deduction += 6
                except Exception:
                    pass

        # 7. Date Format Inconsistencies
        for col in df.columns:
            col_lower = str(col).lower()
            if "date" in col_lower or "time" in col_lower:
                try:
                    pd.to_datetime(df[col], errors="raise")
                except Exception:
                    # Check if parsing with coerce works
                    parsed_coerced = pd.to_datetime(df[col], errors="coerce")
                    failed_dates = parsed_coerced.isnull().sum() - df[col].isnull().sum()
                    if failed_dates > 0:
                        warnings.append(
                            f"Column '{col}' has inconsistent or malformed date formats."
                        )
                        recommendations.append(
                            f"Standardize date fields in '{col}' to a single format (YYYY-MM-DD)."
                        )
                        deduction += 5

        # 8. Constant Columns
        constant_cols = [
            str(c) for c in df.columns if df[c].nunique() == 1 and total_rows > 1
        ]
        if constant_cols:
            warnings.append(
                f"Constant values in columns: {', '.join(constant_cols[:3])}"
            )
            recommendations.append("Review constant columns for variance value.")
            deduction += len(constant_cols) * 2

        # 9. High Cardinality (excluding ID-like fields)
        for col in df.columns:
            col_lower = str(col).lower()
            if "id" not in col_lower and df[col].dtype == "object":
                uniques = df[col].nunique()
                if uniques / total_rows > 0.95 and total_rows > 10:
                    warnings.append(f"High cardinality text column detected: '{col}'.")
                    deduction += 3

        quality_score = max(10, 100 - deduction)

        return {
            "quality_score": quality_score,
            "warnings": warnings,
            "recommendations": recommendations,
        }

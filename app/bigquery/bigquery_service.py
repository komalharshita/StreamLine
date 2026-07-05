import logging
import time
from datetime import datetime, timezone
from typing import Any, Optional
from google.cloud import bigquery
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPIError
from google.api_core.retry import Retry
import pandas as pd

from app.bigquery.config import bq_config
from app.bigquery.exceptions import (
    BigQueryConnectionError,
    JobFailedError,
)
from app.bigquery.schema_detector import SchemaDetector
from app.bigquery.dataset_manager import DatasetManager
from app.bigquery.table_manager import TableManager

logger = logging.getLogger("app.bigquery.bigquery_service")

# Default Retry configurations for transient BigQuery API calls
bq_retry_policy = Retry(
    initial=1.0,
    maximum=10.0,
    multiplier=2.0,
    deadline=60.0,
)
BQ_TIMEOUT_SECONDS = 30.0


class BigQueryService:
    """Core BigQuery service coordinating dataframe schema detection and loading operations."""

    def __init__(self) -> None:
        self.config = bq_config
        self._client: Optional[bigquery.Client] = None

    def _get_client(self) -> bigquery.Client:
        """Lazily instantiates the thread-safe BigQuery Client."""
        if self._client is not None:
            return self._client

        self.config.validate()

        try:
            kwargs = {}
            if self.config.credentials_path:
                logger.info(
                    f"Initializing BigQuery Client using service account path: {self.config.credentials_path}"
                )
                credentials = service_account.Credentials.from_service_account_file(
                    self.config.credentials_path
                )
                kwargs["credentials"] = credentials
            else:
                logger.info(
                    "Initializing BigQuery Client using Application Default Credentials (ADC) / IAM Role."
                )

            kwargs["project"] = self.config.project_id
            self._client = bigquery.Client(**kwargs)
            return self._client

        except Exception as e:
            logger.critical(f"Failed to connect to Google BigQuery: {str(e)}", exc_info=True)
            raise BigQueryConnectionError(
                "Could not connect to Google BigQuery. Authentication or permissions failed.",
                original_exception=e,
            )

    def load_dataframe(
        self,
        df: pd.DataFrame,
        workspace: Optional[str] = None,
        table_name_override: Optional[str] = None,
    ) -> dict[str, Any]:
        """Detects schema, ensures dataset/table exist, and loads DataFrame to BigQuery.

        Returns metadata details: dataset, table, rows, columns, job_id, processing_time.
        """
        start_time = time.perf_counter()
        client = self._get_client()

        # 1. Format dynamic dataset naming: streamline_{workspace}
        workspace_clean = "".join(e for e in (workspace or "default").lower() if e.isalnum())
        dataset_id = f"streamline_{workspace_clean}"

        # 2. Format dynamic table naming: sales_YYYYMMDD_HHMMSS
        timestamp_suffix = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        table_id = table_name_override or f"sales_{timestamp_suffix}"

        logger.info(f"Preparing BigQuery ingestion to target destination: '{dataset_id}.{table_id}'")

        try:
            # 3. Detect and sanitize schema mapping
            schema = SchemaDetector.detect_schema(df)
            
            # Map column names in the DataFrame to their sanitized equivalents
            df_cleaned = df.copy()
            df_cleaned.columns = [SchemaDetector.sanitize_column_name(str(col)) for col in df.columns]

            # 4. Ensure dataset exists
            ds_manager = DatasetManager(client)
            ds_manager.ensure_dataset(dataset_id)

            # 5. Ensure table exists
            t_manager = TableManager(client)
            t_manager.ensure_table(dataset_id, table_id, schema)

            # 6. Configure and trigger the DataFrame Load Job
            table_ref = client.dataset(dataset_id).table(table_id)
            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND",
                schema=schema,
            )

            logger.info(f"Submitting BigQuery Load Job for {len(df_cleaned)} rows...")
            load_job = client.load_table_from_dataframe(
                df_cleaned,
                table_ref,
                job_config=job_config,
                retry=bq_retry_policy,
                timeout=BQ_TIMEOUT_SECONDS,
            )

            # Wait for job execution to finish
            logger.info(f"Awaiting BigQuery Load Job completion: {load_job.job_id}")
            # Maximum 5 minute timeout for full load wait
            load_job.result(timeout=300)

            processing_time_ms = round((time.perf_counter() - start_time) * 1000, 3)
            logger.info(f"Successfully finished BigQuery Load Job: {load_job.job_id}")

            return {
                "dataset": dataset_id,
                "table": table_id,
                "rows": len(df_cleaned),
                "columns": len(df_cleaned.columns),
                "job_id": load_job.job_id,
                "processing_time_ms": processing_time_ms,
            }

        except GoogleAPIError as e:
            logger.error(f"BigQuery load job API failure: {str(e)}", exc_info=True)
            raise JobFailedError(
                f"BigQuery Load Job failed: {str(e)}",
                original_exception=e,
            )
        except Exception as e:
            logger.error(f"Unexpected error loading dataset to BigQuery: {str(e)}", exc_info=True)
            raise JobFailedError(
                f"Unexpected BigQuery load error: {str(e)}",
                original_exception=e,
            )


# Singleton service instance
bq_ingestion_service = BigQueryService()

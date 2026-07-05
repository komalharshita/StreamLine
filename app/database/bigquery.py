import logging
from typing import Any, Mapping, Sequence

from google.cloud import bigquery

from app.database.connection import gcp_client_factory

logger = logging.getLogger("app.database.bigquery")


class BigQueryManager:
    """Wrapper class managing interaction with BigQuery datasets and tables."""

    def __init__(self, client: bigquery.Client = None) -> None:
        # Allow passing custom mock/test client, fall back to default factory
        self.client = client or gcp_client_factory.get_bigquery_client()

    def execute_query(
        self, query: str, job_config: bigquery.QueryJobConfig = None
    ) -> bigquery.table.RowIterator:
        """Executes a SQL query against BigQuery.

        Returns a RowIterator to process results.
        """
        logger.debug(f"Running BigQuery query: {query}")
        try:
            query_job = self.client.query(query, job_config=job_config)
            # Wait for query to finish
            results = query_job.result()
            return results
        except Exception as e:
            logger.error(f"BigQuery query execution failed: {str(e)}")
            raise e

    def insert_rows_json(
        self, dataset_id: str, table_id: str, json_rows: Sequence[Mapping[str, Any]]
    ) -> Sequence[dict[str, Any]]:
        """Performs a streaming insert of JSON rows into a BigQuery table.

        Returns a list of errors if any occurred, empty list otherwise.
        """
        logger.debug(f"Streaming {len(json_rows)} rows into {dataset_id}.{table_id}")
        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            errors = self.client.insert_rows_json(table_ref, json_rows)
            if errors:
                logger.error(f"BigQuery streaming insert returned errors: {errors}")
            return errors
        except Exception as e:
            logger.error(f"BigQuery streaming insert failed: {str(e)}")
            raise e

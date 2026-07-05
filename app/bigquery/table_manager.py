import logging

from google.api_core.exceptions import Conflict, NotFound
from google.cloud import bigquery

logger = logging.getLogger("app.bigquery.table_manager")


class TableManager:
    """Manages check existence and schema creation operations of BigQuery Tables."""

    def __init__(self, client: bigquery.Client) -> None:
        self.client = client

    def ensure_table(
        self,
        dataset_id: str,
        table_id: str,
        schema: list[bigquery.SchemaField],
    ) -> bigquery.Table:
        """Verifies if a table exists, and creates it dynamically using the detected schema layout if missing."""
        dataset_ref = self.client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_id)

        try:
            # Check if table exists
            table = self.client.get_table(table_ref)
            logger.info(
                f"BigQuery table '{dataset_id}.{table_id}' verified (already exists)."
            )
            return table
        except NotFound:
            logger.info(
                f"BigQuery table '{dataset_id}.{table_id}' not found. Initializing creation."
            )
            try:
                new_table = bigquery.Table(table_ref, schema=schema)
                created_table = self.client.create_table(new_table, timeout=30)
                logger.info(
                    f"Successfully created BigQuery table: '{dataset_id}.{table_id}'"
                )
                return created_table
            except Conflict:
                # Catch concurrent table creation race conditions
                logger.warning(
                    f"BigQuery table '{dataset_id}.{table_id}' was created concurrently by another process."
                )
                return self.client.get_table(table_ref)
            except Exception as e:
                logger.error(
                    f"Failed to create BigQuery table '{dataset_id}.{table_id}': {str(e)}",
                    exc_info=True,
                )
                raise

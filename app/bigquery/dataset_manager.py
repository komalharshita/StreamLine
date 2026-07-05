import logging

from google.api_core.exceptions import Conflict, NotFound
from google.cloud import bigquery

logger = logging.getLogger("app.bigquery.dataset_manager")


class DatasetManager:
    """Manages check existence and dynamic creation operations of BigQuery Datasets."""

    def __init__(self, client: bigquery.Client) -> None:
        self.client = client

    def ensure_dataset(self, dataset_id: str, location: str = "US") -> bigquery.Dataset:
        """Verifies if a dataset exists, and creates it dynamically if missing."""
        dataset_ref = self.client.dataset(dataset_id)

        try:
            # Check if dataset exists
            dataset = self.client.get_dataset(dataset_ref)
            logger.info(f"BigQuery dataset '{dataset_id}' verified (already exists).")
            return dataset
        except NotFound:
            logger.info(
                f"BigQuery dataset '{dataset_id}' not found. Initializing creation."
            )
            try:
                new_dataset = bigquery.Dataset(dataset_ref)
                new_dataset.location = location
                created_dataset = self.client.create_dataset(new_dataset, timeout=30)
                logger.info(
                    f"Successfully created BigQuery dataset: '{dataset_id}' in location: '{location}'"
                )
                return created_dataset
            except Conflict:
                # Catch race conditions where another thread/process created it concurrently
                logger.warning(
                    f"BigQuery dataset '{dataset_id}' was created concurrently by another process."
                )
                return self.client.get_dataset(dataset_ref)
            except Exception as e:
                logger.error(
                    f"Failed to create BigQuery dataset '{dataset_id}': {str(e)}",
                    exc_info=True,
                )
                raise

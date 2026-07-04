class BigQueryError(Exception):
    """Base exception for all BigQuery ingestion operations."""

    def __init__(self, message: str, original_exception: Exception = None) -> None:
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception


class BigQueryConfigurationError(BigQueryError):
    """Raised when BigQuery settings fail validation checks."""

    pass


class BigQueryConnectionError(BigQueryError):
    """Raised when client initialization or authentication with BigQuery fails."""

    pass


class SchemaDetectionError(BigQueryError):
    """Raised when detecting the schema layout from a DataFrame fails."""

    pass


class JobFailedError(BigQueryError):
    """Raised when a BigQuery load job fails or returns error statuses."""

    pass

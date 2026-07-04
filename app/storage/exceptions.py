class StorageError(Exception):
    """Base exception for all GCS storage operations."""

    def __init__(self, message: str, original_exception: Exception = None) -> None:
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception


class StorageConfigurationError(StorageError):
    """Raised when GCS configurations or credentials fail validation checks."""

    pass


class StorageConnectionError(StorageError):
    """Raised when connecting or authenticating with Google Cloud Storage services fails."""

    pass


class StorageUploadError(StorageError):
    """Raised when a blob upload operation fails or times out."""

    pass


class StorageDeleteError(StorageError):
    """Raised when a blob deletion operation fails."""

    pass

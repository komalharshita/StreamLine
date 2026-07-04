from abc import ABC, abstractmethod
from typing import Generic, Optional, Sequence, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository defining standard CRUD and query operations."""

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        """Retrieves a single domain entity by its unique ID."""
        pass

    @abstractmethod
    def list_all(self) -> Sequence[T]:
        """Retrieves all domain entities."""
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        """Saves a new domain entity or updates an existing one."""
        pass

    @abstractmethod
    def delete_by_id(self, id: str) -> None:
        """Deletes a domain entity by its unique ID."""
        pass

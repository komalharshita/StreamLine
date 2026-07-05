import logging
from typing import Any

logger = logging.getLogger("app.upload.status_tracker")

# In-memory status store mapping upload_id to its stage and progress percentage
_status_store: dict[str, dict[str, Any]] = {}


class UploadStatusTracker:
    """Manages the in-memory state tracking for active dataset processing stages."""

    @staticmethod
    def initialize_status(upload_id: str) -> None:
        _status_store[upload_id] = {
            "status": "Uploading",
            "stage": "Uploading File",
            "progress": 10,
            "error": None,
        }
        logger.info(f"Initialized upload tracking for ID: {upload_id}")

    @staticmethod
    def update_status(upload_id: str, status: str, stage: str, progress: int) -> None:
        if upload_id in _status_store:
            _status_store[upload_id].update({
                "status": status,
                "stage": stage,
                "progress": progress,
            })
            logger.info(f"Upload '{upload_id}' stage updated: {stage} ({progress}%)")

    @staticmethod
    def fail_status(upload_id: str, error_msg: str) -> None:
        if upload_id in _status_store:
            _status_store[upload_id].update({
                "status": "Failed",
                "stage": "Failed",
                "progress": 0,
                "error": error_msg,
            })
            logger.error(f"Upload '{upload_id}' failed: {error_msg}")

    @staticmethod
    def get_status(upload_id: str) -> dict[str, Any]:
        return _status_store.get(
            upload_id,
            {
                "status": "Unknown",
                "stage": "Not Found",
                "progress": 0,
                "error": "Upload ID not found in tracker.",
            },
        )

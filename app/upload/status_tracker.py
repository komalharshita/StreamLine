import logging
import time
from typing import Any

logger = logging.getLogger("app.upload.status_tracker")

# In-memory status store mapping upload_id to its stage and progress percentage
_status_store: dict[str, dict[str, Any]] = {}


class UploadStatusTracker:
    """Manages the in-memory state tracking for active dataset processing stages."""

    @staticmethod
    def initialize_status(upload_id: str) -> None:
        _status_store[upload_id] = {
            "status": "UPLOADING",
            "stage": "Uploading File",
            "progress": 10,
            "start_time": time.time(),
            "completed_steps": [],
            "error": None,
        }
        logger.info(f"Initialized upload tracking for ID: {upload_id}")

    @staticmethod
    def update_status(upload_id: str, status: str, stage: str, progress: int) -> None:
        if upload_id in _status_store:
            record = _status_store[upload_id]
            # Track completed steps dynamically
            completed = record.get("completed_steps", [])
            if status not in completed and status not in ("FAILED", "COMPLETED"):
                completed.append(status)

            record.update(
                {
                    "status": status,
                    "stage": stage,
                    "progress": progress,
                    "completed_steps": completed,
                }
            )
            logger.info(f"Upload '{upload_id}' stage updated: {stage} ({progress}%)")

    @staticmethod
    def fail_status(upload_id: str, error_msg: str) -> None:
        if upload_id in _status_store:
            _status_store[upload_id].update(
                {
                    "status": "FAILED",
                    "stage": "Failed",
                    "progress": 0,
                    "error": error_msg,
                }
            )
            logger.error(f"Upload '{upload_id}' failed: {error_msg}")

    @staticmethod
    def get_status(upload_id: str) -> dict[str, Any]:
        record = _status_store.get(upload_id)
        if not record:
            return {
                "status": "FAILED",
                "stage": "Not Found",
                "progress": 0,
                "estimated_time_remaining": "0 seconds",
                "elapsed_time": "0 seconds",
                "completed_steps": [],
                "error": "Upload ID not found in tracker.",
            }

        status = record.get("status", "UPLOADING")
        progress = record.get("progress", 0)
        start_time = record.get("start_time", time.time())
        elapsed_sec = int(time.time() - start_time)
        elapsed_time = f"{elapsed_sec} seconds"

        # Dynamically estimate remaining time based on granular state
        estimators = {
            "UPLOADING": "10 seconds",
            "VALIDATING": "8 seconds",
            "PARSING": "6 seconds",
            "ANALYZING": "4 seconds",
            "GENERATING_PREVIEW": "2 seconds",
            "WAITING_CONFIRMATION": "0 seconds",
            "IMPORTING": "20 seconds",
            "UPLOADING_TO_BIGQUERY": "12 seconds",
            "RUNNING_DECISION_ENGINE": "5 seconds",
            "GENERATING_METADATA": "1 second",
            "COMPLETED": "0 seconds",
            "FAILED": "0 seconds",
        }
        est_remaining = estimators.get(status, "0 seconds")

        return {
            "status": status,
            "stage": record.get("stage", "Processing"),
            "progress": progress,
            "estimated_time_remaining": est_remaining,
            "elapsed_time": elapsed_time,
            "completed_steps": record.get("completed_steps", []),
            "error": record.get("error"),
        }

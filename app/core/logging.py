import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Custom formatter to output logs in structured JSON format for Cloud logging."""

    def format(self, record: logging.LogRecord) -> str:
        # Construct standard structured payload
        log_record: dict[str, Any] = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "logging.googleapis.com/sourceLocation": {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            },
        }

        # Include traceback details if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Include custom extra variables passed to the log
        if hasattr(record, "extra_fields"):
            log_record.update(record.extra_fields)  # type: ignore

        return json.dumps(log_record)


def setup_logging() -> logging.Logger:
    """Sets up global application logging configuration."""
    logger = logging.getLogger()
    
    # Remove default handlers to prevent duplicate logs
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Output to stdout
    handler = logging.StreamHandler(sys.stdout)

    if settings.ENVIRONMENT == "production":
        # Format logs as structured JSON for production Cloud environments
        handler.setFormatter(JSONFormatter())
    else:
        # Human-readable format for local development
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] (%(name)s:%(filename)s:%(lineno)d) - %(message)s"
        )
        handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.getLevelName(settings.LOG_LEVEL.upper()))

    # Suppress verbose default logs from external libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    return logger

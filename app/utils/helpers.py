import re
from datetime import datetime, timezone


def get_utc_now() -> datetime:
    """Returns the current date and time in UTC format."""
    return datetime.now(timezone.utc)


def sanitize_filename(filename: str) -> str:
    """Sanitizes a input file name.

    Removes special characters and replaces spaces with underscores.
    """
    # Keep only letters, digits, dots, underscores, and dashes
    filename = re.sub(r"[^\w\.\-]", "_", filename)
    # Remove leading dots/dashes
    filename = filename.lstrip(".-")
    return filename or "unnamed_file"

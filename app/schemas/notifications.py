from datetime import datetime

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """Response payload detailing a single user notification."""

    id: str
    recipient_id: str
    title: str
    message: str
    read: bool
    created_at: datetime


class MarkReadRequest(BaseModel):
    """Payload to mark selected notifications as read."""

    notification_ids: list[str] = Field(
        ..., description="Identifiers of notifications to update"
    )


class MarkReadResponse(BaseModel):
    """Confirmation payload returned after marking notifications read."""

    updated_count: int = Field(
        ..., description="Number of notifications successfully marked read"
    )
    success: bool = True

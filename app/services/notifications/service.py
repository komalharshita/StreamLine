import logging
import uuid
from abc import ABC, abstractmethod
from typing import Sequence

from app.models.domain import PlatformNotification
from app.schemas.notifications import MarkReadRequest, MarkReadResponse
from app.services.base import BaseService

logger = logging.getLogger("app.services.notifications")


class NotificationsServiceInterface(BaseService, ABC):
    """Interface for sending and updating workspace notifications."""

    @abstractmethod
    def dispatch_notification(
        self, recipient_id: str, title: str, message: str
    ) -> PlatformNotification:
        """Sends and logs a notification to a specific user."""
        pass

    @abstractmethod
    def mark_notifications_read(
        self, request: MarkReadRequest, user_id: str
    ) -> MarkReadResponse:
        """Marks a subset of user notifications as read."""
        pass

    @abstractmethod
    def list_user_notifications(self, user_id: str) -> Sequence[PlatformNotification]:
        """Lists notifications for a specific recipient user."""
        pass


class NotificationsService(NotificationsServiceInterface):
    """Concrete implementation of NotificationsService."""

    def __init__(self) -> None:
        # Mock database storage since we aren't using a persistent relational DB yet
        self._notifications: list[PlatformNotification] = []

    def dispatch_notification(
        self, recipient_id: str, title: str, message: str
    ) -> PlatformNotification:
        logger.info(f"Dispatching notification '{title}' to user: {recipient_id}")

        notification = PlatformNotification(
            id=f"notif-{uuid.uuid4()}",
            recipient_id=recipient_id,
            title=title,
            message=message,
            read=False,
        )
        self._notifications.append(notification)

        # In production, this would publish a message to Google Cloud Pub/Sub or AWS SNS
        logger.debug(f"Notification {notification.id} published to active subscribers.")
        return notification

    def mark_notifications_read(
        self, request: MarkReadRequest, user_id: str
    ) -> MarkReadResponse:
        logger.info(
            f"Marking {len(request.notification_ids)} notifications read for user {user_id}"
        )
        count = 0
        for notif in self._notifications:
            if notif.recipient_id == user_id and notif.id in request.notification_ids:
                if not notif.read:
                    notif.read = True
                    count += 1
        return MarkReadResponse(updated_count=count, success=True)

    def list_user_notifications(self, user_id: str) -> Sequence[PlatformNotification]:
        logger.debug(f"Listing notifications for recipient: {user_id}")
        return [n for n in self._notifications if n.recipient_id == user_id]

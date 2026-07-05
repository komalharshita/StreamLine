from typing import Any, Sequence

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_notifications_service
from app.schemas.notifications import (
    MarkReadRequest,
    MarkReadResponse,
    NotificationResponse,
)
from app.services.notifications.service import NotificationsServiceInterface

router = APIRouter()


@router.get("/all", response_model=list[NotificationResponse])
def get_all_notifications(
    current_user: dict[str, Any] = Depends(get_current_user),
    notif_service: NotificationsServiceInterface = Depends(get_notifications_service),
) -> Sequence[Any]:
    """Retrieves all notifications dispatched to the current authenticated user."""
    user_id = current_user.get("uid", "anonymous")
    notifications = notif_service.list_user_notifications(user_id)
    return [NotificationResponse.model_validate(n) for n in notifications]


@router.get("/unread", response_model=list[NotificationResponse])
def get_unread_notifications(
    current_user: dict[str, Any] = Depends(get_current_user),
    notif_service: NotificationsServiceInterface = Depends(get_notifications_service),
) -> Sequence[Any]:
    """Retrieves only unread notifications."""
    user_id = current_user.get("uid", "anonymous")
    notifications = notif_service.list_user_notifications(user_id)
    return [NotificationResponse.model_validate(n) for n in notifications if not n.read]


@router.post("/read", response_model=MarkReadResponse)
def mark_notifications_as_read(
    request: MarkReadRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    notif_service: NotificationsServiceInterface = Depends(get_notifications_service),
) -> MarkReadResponse:
    """Marks a list of specified notification logs as read."""
    user_id = current_user.get("uid", "anonymous")
    return notif_service.mark_notifications_read(request, user_id)

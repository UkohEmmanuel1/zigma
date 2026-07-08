import logging

from notifications.models import Notification

logger = logging.getLogger(__name__)

NOTIFICATION_TYPES = {
    "order_filled": {"title": "Order Filled", "icon": "check_circle"},
    "order_rejected": {"title": "Order Rejected", "icon": "cancel"},
    "order_cancelled": {"title": "Order Cancelled", "icon": "remove_circle"},
}


def create_notification(user, type, title=None, message="", related_object_type=None, related_object_id=None):
    if title is None and type in NOTIFICATION_TYPES:
        title = NOTIFICATION_TYPES[type]["title"]

    notification = Notification.objects.create(
        user=user,
        type=type,
        title=title,
        message=message,
        related_object_type=related_object_type,
        related_object_id=related_object_id,
    )
    logger.debug("Notification %s created for %s", notification.id, user.email)
    return notification

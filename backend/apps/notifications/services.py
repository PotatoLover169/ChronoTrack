from apps.notifications.models import Notification


def create_notification(
    recipient,
    notification_type,
    title,
    message,
):
    """
    Create a notification for a user.
    """

    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
    )


def get_notifications(user):
    """
    Return all notifications for the user.
    """

    return Notification.objects.filter(
        recipient=user,
    )


def get_unread_notifications(user):
    """
    Return unread notifications.
    """

    return Notification.objects.filter(
        recipient=user,
        is_read=False,
    )


def mark_notification_as_read(
    notification,
):
    """
    Mark a notification as read.
    """

    notification.is_read = True
    notification.save(
        update_fields=["is_read"],
    )

    return notification


def mark_all_notifications_as_read(
    user,
):
    """
    Mark all notifications as read.
    """

    return Notification.objects.filter(
        recipient=user,
        is_read=False,
    ).update(
        is_read=True,
    )
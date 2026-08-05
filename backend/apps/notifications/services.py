from apps.notifications.models import Notification


# ======================================================
# Generic Notification Creator
# ======================================================

def create_notification(
    recipient,
    notification_type,
    title,
    message,
):
    """
    Create a notification.
    """

    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
    )


# ======================================================
# Task Notifications
# ======================================================

def notify_task_created(
    recipient,
    task,
):
    """
    Notify user when a task is created.
    """

    return create_notification(
        recipient=recipient,
        notification_type="task",
        title="New Task Created",
        message=f"{task.title} has been created successfully.",
    )


def notify_task_completed(
    recipient,
    task,
):
    """
    Notify user when a task is completed.
    """

    return create_notification(
        recipient=recipient,
        notification_type="task",
        title="Task Completed",
        message=f"{task.title} has been completed.",
    )


# ======================================================
# Notification Queries
# ======================================================

def get_notifications(user):
    """
    Return all notifications.
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
    Mark notification as read.
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
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
# Project Notifications
# ======================================================

def notify_project_created(
    recipient,
    project,
):
    """
    Notify user when a project is created.
    """

    return create_notification(
        recipient=recipient,
        notification_type="project",
        title="New Project Created",
        message=f"{project.name} has been created successfully.",
    )


def notify_project_completed(
    recipient,
    project,
):
    """
    Notify user when a project is completed.
    """

    return create_notification(
        recipient=recipient,
        notification_type="project",
        title="Project Completed",
        message=f"{project.name} has been completed.",
    )


# ======================================================
# Tracker Notifications
# ======================================================

def notify_timer_started(
    recipient,
    time_entry,
):
    """
    Notify user when a timer starts.
    """

    return create_notification(
        recipient=recipient,
        notification_type="tracker",
        title="Timer Started",
        message=f"Timer started for {time_entry.project.name}.",
    )


def notify_timer_stopped(
    recipient,
    time_entry,
):
    """
    Notify user when a timer stops.
    """

    return create_notification(
        recipient=recipient,
        notification_type="tracker",
        title="Timer Stopped",
        message=f"Timer stopped for {time_entry.project.name}.",
    )


def notify_time_entry_updated(
    recipient,
    time_entry,
):
    """
    Notify user when a time entry is updated.
    """

    return create_notification(
        recipient=recipient,
        notification_type="tracker",
        title="Time Entry Updated",
        message=f"Time entry for {time_entry.project.name} has been updated.",
    )


def notify_time_entry_deleted(
    recipient,
    time_entry,
):
    """
    Notify user when a time entry is deleted.
    """

    return create_notification(
        recipient=recipient,
        notification_type="tracker",
        title="Time Entry Deleted",
        message=f"Time entry for {time_entry.project.name} has been deleted.",
    )

# ======================================================
# Approval Notifications
# ======================================================

def notify_edit_request_submitted(
    recipient,
    edit_request,
):
    """
    Notify user that an edit request has been submitted.
    """

    return create_notification(
        recipient=recipient,
        notification_type="approval",
        title="Edit Request Submitted",
        message=(
            f"Your request to edit Time Entry "
            f"#{edit_request.time_entry.id} has been submitted."
        ),
    )


def notify_edit_request_approved(
    recipient,
    edit_request,
):
    """
    Notify user that an edit request has been approved.
    """

    return create_notification(
        recipient=recipient,
        notification_type="approval",
        title="Edit Request Approved",
        message=(
            f"Your request for Time Entry "
            f"#{edit_request.time_entry.id} has been approved."
        ),
    )


def notify_edit_request_rejected(
    recipient,
    edit_request,
):
    """
    Notify user that an edit request has been rejected.
    """

    return create_notification(
        recipient=recipient,
        notification_type="approval",
        title="Edit Request Rejected",
        message=(
            f"Your request for Time Entry "
            f"#{edit_request.time_entry.id} has been rejected."
        ),
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
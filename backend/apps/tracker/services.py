from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.notifications.services import (
    notify_timer_started,
    notify_timer_stopped,
)

from .exceptions import (
    NoRunningTimerError,
    TimerAlreadyRunningError,
)
from .models import (
    TimeEntry,
    TimeEntryStatus,
)


def is_manager_or_admin(user):
    """
    Return True when the user has Manager or Admin privileges.
    """

    return (
        user.is_superuser
        or user.groups.filter(
            name__in=["Manager", "Admin"]
        ).exists()
    )


def validate_timer_access(
    *,
    user,
    project,
    task=None,
):
    """
    Validate whether a user is allowed to track time
    against the selected project and task.

    Rules:

    Manager/Admin:
        - May track time on any project.
        - May track time on any task belonging to that project.

    Employee:
        - Must be a member of the project.
        - If a task is provided, the task must belong
          to the selected project.
        - If a task is provided, the employee must be
          assigned to that task.
    """

    # --------------------------------------------------
    # 1. Manager/Admin access
    # --------------------------------------------------

    if is_manager_or_admin(user):

        if task and task.project_id != project.id:
            raise ValidationError(
                {
                    "task": (
                        "The selected task does not belong "
                        "to the selected project."
                    )
                }
            )

        return


    # --------------------------------------------------
    # 2. Employee project access
    # --------------------------------------------------

    if not project.members.filter(
        id=user.id
    ).exists():

        raise ValidationError(
            {
                "project": (
                    "You are not assigned to this project."
                )
            }
        )


    # --------------------------------------------------
    # 3. Employee task validation
    # --------------------------------------------------

    if task:

        if task.project_id != project.id:
            raise ValidationError(
                {
                    "task": (
                        "The selected task does not belong "
                        "to the selected project."
                    )
                }
            )

        if task.assigned_to_id != user.id:
            raise ValidationError(
                {
                    "task": (
                        "You are not assigned to this task."
                    )
                }
            )


def start_timer(
    *,
    user,
    project,
    task=None,
    description="",
):
    """
    Start a new timer for a user.

    Business rules are validated before the TimeEntry
    is created.
    """

    with transaction.atomic():

        # --------------------------------------------------
        # 1. Prevent multiple running timers
        # --------------------------------------------------

        running_timer = (
            TimeEntry.objects
            .filter(
                owner=user,
                status=TimeEntryStatus.RUNNING,
            )
            .first()
        )

        if running_timer:
            raise TimerAlreadyRunningError()


        # --------------------------------------------------
        # 2. Validate project/task access
        # --------------------------------------------------

        validate_timer_access(
            user=user,
            project=project,
            task=task,
        )


        # --------------------------------------------------
        # 3. Create the timer
        # --------------------------------------------------

        time_entry = TimeEntry.objects.create(
            owner=user,
            project=project,
            task=task,
            description=description,
            start_time=timezone.now(),
            status=TimeEntryStatus.RUNNING,
        )


        # --------------------------------------------------
        # 4. Notify user
        # --------------------------------------------------

        notify_timer_started(
            recipient=user,
            time_entry=time_entry,
        )


        return time_entry


def stop_timer(
    *,
    user,
):
    """
    Stop the user's currently running timer.
    """

    with transaction.atomic():

        time_entry = (
            TimeEntry.objects
            .filter(
                owner=user,
                status=TimeEntryStatus.RUNNING,
            )
            .first()
        )

        if not time_entry:
            raise NoRunningTimerError()


        # --------------------------------------------------
        # Complete timer
        # --------------------------------------------------

        time_entry.end_time = timezone.now()
        time_entry.status = TimeEntryStatus.COMPLETED

        time_entry.save()


        # --------------------------------------------------
        # Notify user
        # --------------------------------------------------

        notify_timer_stopped(
            recipient=user,
            time_entry=time_entry,
        )


        return time_entry


def get_current_timer(
    *,
    user,
):
    """
    Return the user's currently running timer.
    """

    return (
        TimeEntry.objects
        .filter(
            owner=user,
            status=TimeEntryStatus.RUNNING,
        )
        .select_related(
            "project",
            "task",
        )
        .first()
    )
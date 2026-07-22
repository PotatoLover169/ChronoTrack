from django.db import transaction
from django.utils import timezone

from .exceptions import (
    NoRunningTimerError,
    TimerAlreadyRunningError,
)
from .models import TimeEntry, TimeEntryStatus


def start_timer(
    *,
    user,
    project,
    task=None,
    description="",
):
    """
    Start a new timer for a user.
    """

    with transaction.atomic():

        running_timer = TimeEntry.objects.filter(
            owner=user,
            status=TimeEntryStatus.RUNNING,
        ).first()

        if running_timer:
            raise TimerAlreadyRunningError()

        time_entry = TimeEntry.objects.create(
            owner=user,
            project=project,
            task=task,
            description=description,
            start_time=timezone.now(),
            status=TimeEntryStatus.RUNNING,
        )

        return time_entry

def stop_timer(*, user):
    """
    Stop the user's currently running timer.
    """

    with transaction.atomic():

        time_entry = TimeEntry.objects.filter(
            owner=user,
            status=TimeEntryStatus.RUNNING,
        ).first()

        if not time_entry:
            raise NoRunningTimerError()

        time_entry.end_time = timezone.now()
        time_entry.status = TimeEntryStatus.COMPLETED
        time_entry.save()

        return time_entry

def get_current_timer(*, user):
    """
    Return the user's currently running timer.
    """

    return TimeEntry.objects.filter(
        owner=user,
        status=TimeEntryStatus.RUNNING,
    ).select_related(
        "project",
        "task",
    ).first()
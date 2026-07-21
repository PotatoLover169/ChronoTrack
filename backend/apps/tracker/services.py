from django.db import transaction
from django.utils import timezone

from .exceptions import TimerAlreadyRunningError
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
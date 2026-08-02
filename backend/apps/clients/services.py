from decimal import Decimal

from apps.clients.models import Client
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.tracker.models import (
    TimeEntry,
    TimeEntryStatus,
)


def get_client_dashboard(
    *,
    user,
    client_id,
):
    """
    Return dashboard statistics for a client.
    """

    client = Client.objects.get(
        id=client_id,
        owner=user,
    )

    projects = Project.objects.filter(
        owner=user,
        client=client,
    )

    tasks = Task.objects.filter(
        owner=user,
        project__client=client,
    )

    entries = (
        TimeEntry.objects.filter(
            owner=user,
            project__client=client,
            status=TimeEntryStatus.COMPLETED,
        )
        .select_related(
            "project",
            "task",
        )
    )

    total_projects = projects.count()

    active_projects = projects.filter(
        status="in_progress",
    ).count()

    completed_projects = projects.filter(
        status="completed",
    ).count()

    total_tasks = tasks.count()

    completed_tasks = tasks.filter(
        status="completed",
    ).count()

    total_entries = entries.count()

    total_hours = Decimal("0.00")
    billable_hours = Decimal("0.00")
    non_billable_hours = Decimal("0.00")
    total_earnings = Decimal("0.00")

    for entry in entries:

        if not entry.duration:
            continue

        hours = Decimal(
            str(
                entry.duration.total_seconds() / 3600
            )
        )

        total_hours += hours

        if entry.billable:
            billable_hours += hours
        else:
            non_billable_hours += hours

        total_earnings += entry.earnings

    return {
        "client": client,
        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "total_entries": total_entries,
        "total_hours": total_hours.quantize(
            Decimal("0.01")
        ),
        "billable_hours": billable_hours.quantize(
            Decimal("0.01")
        ),
        "non_billable_hours": non_billable_hours.quantize(
            Decimal("0.01")
        ),
        "total_earnings": total_earnings.quantize(
            Decimal("0.01")
        ),
    }
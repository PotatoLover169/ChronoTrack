from decimal import Decimal

from django.db import models

from apps.clients.models import Client
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.tracker.models import (
    TimeEntry,
    TimeEntryStatus,
)


def is_manager_or_admin(user):
    return (
        user.is_superuser
        or user.groups.filter(
            name__in=["Admin", "Manager"]
        ).exists()
    )


def get_accessible_projects(
    *,
    user,
    client,
):
    """
    Return projects for the selected client that the user
    is allowed to access.
    """

    if is_manager_or_admin(user):
        return Project.objects.filter(
            client=client,
        )

    return Project.objects.filter(
        client=client,
    ).filter(
        models.Q(owner=user)
        | models.Q(members=user)
    ).distinct()


def get_client_dashboard(
    *,
    user,
    client_id,
):
    """
    Return dashboard statistics for a client.

    Managers and Admins:
        - Can view organization-wide statistics for the client.

    Employees:
        - Can view statistics for projects they own or
          are assigned to.
    """

    if is_manager_or_admin(user):
        client = Client.objects.get(
            id=client_id,
        )
    else:
        client = Client.objects.filter(
            id=client_id,
        ).filter(
            models.Q(projects__owner=user)
            | models.Q(projects__members=user)
            | models.Q(owner=user)
        ).distinct().first()

        if not client:
            raise Client.DoesNotExist

    projects = get_accessible_projects(
        user=user,
        client=client,
    )

    tasks = Task.objects.filter(
        project__in=projects,
    )

    entries = (
        TimeEntry.objects.filter(
            project__in=projects,
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
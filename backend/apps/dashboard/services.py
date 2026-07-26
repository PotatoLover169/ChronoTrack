from decimal import Decimal

from django.utils import timezone

from apps.approvals.models import (
    EditRequestStatus,
    TimeEntryEditRequest,
)
from apps.clients.models import Client
from apps.projects.models import Project
from apps.tracker.models import (
    TimeEntry,
    TimeEntryStatus,
)


def get_completed_entries(user):
    """
    Returns all completed time entries for the user.
    """
    return TimeEntry.objects.filter(
        owner=user,
        status=TimeEntryStatus.COMPLETED,
    )


def get_running_timer(user):
    return TimeEntry.objects.filter(
        owner=user,
        status=TimeEntryStatus.RUNNING,
    ).exists()


def get_today_hours(user):
    today = timezone.localdate()

    total_seconds = 0

    entries = get_completed_entries(user).filter(
        start_time__date=today,
    )

    for entry in entries:
        if entry.duration:
            total_seconds += entry.duration.total_seconds()

    return round(total_seconds / 3600, 2)


def get_this_week_hours(user):
    today = timezone.localdate()

    week_start = today - timezone.timedelta(days=today.weekday())

    total_seconds = 0

    entries = get_completed_entries(user).filter(
        start_time__date__gte=week_start,
    )

    for entry in entries:
        if entry.duration:
            total_seconds += entry.duration.total_seconds()

    return round(total_seconds / 3600, 2)


def get_this_month_hours(user):
    today = timezone.localdate()

    total_seconds = 0

    entries = get_completed_entries(user).filter(
        start_time__year=today.year,
        start_time__month=today.month,
    )

    for entry in entries:
        if entry.duration:
            total_seconds += entry.duration.total_seconds()

    return round(total_seconds / 3600, 2)


def get_billable_hours(user):
    total_seconds = 0

    entries = get_completed_entries(user).filter(
        billable=True,
    )

    for entry in entries:
        if entry.duration:
            total_seconds += entry.duration.total_seconds()

    return round(total_seconds / 3600, 2)


def get_estimated_earnings(user):
    total = Decimal("0.00")

    for entry in get_completed_entries(user):
        total += entry.earnings

    return total


def get_active_projects(user):
    return Project.objects.filter(
        owner=user,
        status="in_progress",
    ).count()


def get_completed_projects(user):
    return Project.objects.filter(
        owner=user,
        status="completed",
    ).count()


def get_total_clients(user):
    return Client.objects.filter(
        owner=user,
    ).count()


def get_pending_approvals():
    return TimeEntryEditRequest.objects.filter(
        status=EditRequestStatus.PENDING,
    ).count()

def get_recent_entries(
    user,
    limit=5,
):
    """
    Return the most recent completed time entries.
    """

    return (
        get_completed_entries(user)
        .select_related(
            "project",
            "task",
        )
        .order_by("-start_time")[:limit]
    )

from collections import defaultdict


def get_top_projects(
    user,
    limit=5,
):
    """
    Return the projects with the highest tracked hours.
    """

    project_data = defaultdict(
        lambda: {
            "project": None,
            "hours": 0,
            "earnings": Decimal("0.00"),
        }
    )

    entries = get_completed_entries(user).select_related(
        "project",
    )

    for entry in entries:
        project = entry.project

        item = project_data[project.id]

        item["project"] = project

        if entry.duration:
            item["hours"] += (
                entry.duration.total_seconds() / 3600
            )

        item["earnings"] += entry.earnings

    projects = sorted(
        project_data.values(),
        key=lambda x: x["hours"],
        reverse=True,
    )

    return projects[:limit]

def get_hours_per_day(
    user,
    days=7,
):
    """
    Return tracked hours for each of the last N days.
    """

    today = timezone.localdate()

    results = []

    for i in range(days - 1, -1, -1):
        current_day = today - timezone.timedelta(
            days=i,
        )

        total_seconds = 0

        entries = (
            get_completed_entries(user)
            .filter(
                start_time__date=current_day,
            )
        )

        for entry in entries:
            if entry.duration:
                total_seconds += (
                    entry.duration.total_seconds()
                )

        results.append(
            {
                "date": current_day.isoformat(),
                "hours": round(
                    total_seconds / 3600,
                    2,
                ),
            }
        )

    return results

def get_billable_breakdown(
    user,
):
    """
    Return billable and non-billable tracked hours.
    """

    billable_seconds = 0
    non_billable_seconds = 0

    entries = get_completed_entries(user)

    for entry in entries:
        if not entry.duration:
            continue

        seconds = entry.duration.total_seconds()

        if entry.billable:
            billable_seconds += seconds
        else:
            non_billable_seconds += seconds

    return {
        "billable_hours": round(
            billable_seconds / 3600,
            2,
        ),
        "non_billable_hours": round(
            non_billable_seconds / 3600,
            2,
        ),
    }

def get_dashboard_data(user):
    """
    Return dashboard statistics.
    """

    return {
            "summary": {
                "running_timer": get_running_timer(user),
                "today_hours": get_today_hours(user),
                "this_week_hours": get_this_week_hours(user),
                "this_month_hours": get_this_month_hours(user),
                "active_projects": get_active_projects(user),
                "completed_projects": get_completed_projects(user),
                "total_clients": get_total_clients(user),
                "billable_hours": get_billable_hours(user),
                "estimated_earnings": get_estimated_earnings(user),
                "pending_approvals": get_pending_approvals(),
        },
        "recent_entries": get_recent_entries(user),
        
        "top_projects": get_top_projects(user),

        "hours_per_day": get_hours_per_day(user),

        "billable_breakdown": get_billable_breakdown(user),
    }
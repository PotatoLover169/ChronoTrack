from calendar import month_name
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.projects.models import Project
from apps.tracker.models import (
    TimeEntry,
    TimeEntryStatus,
)


def get_completed_entries(user):
    """
    Return all completed time entries for the user.
    """

    return TimeEntry.objects.filter(
        owner=user,
        status=TimeEntryStatus.COMPLETED,
    )


def get_report_summary(user):
    """
    Return summary statistics for reports.
    """

    entries = get_completed_entries(user)

    total_entries = entries.count()

    completed_entries = total_entries

    billable_entries = entries.filter(
        billable=True,
    ).count()

    non_billable_entries = entries.filter(
        billable=False,
    ).count()

    total_seconds = 0
    billable_seconds = 0
    estimated_earnings = Decimal("0.00")

    for entry in entries:

        if entry.duration:

            seconds = entry.duration.total_seconds()

            total_seconds += seconds

            if entry.billable:
                billable_seconds += seconds

        estimated_earnings += entry.earnings

    return {
        "total_entries": total_entries,
        "completed_entries": completed_entries,
        "billable_entries": billable_entries,
        "non_billable_entries": non_billable_entries,
        "total_duration_hours": round(
            total_seconds / 3600,
            2,
        ),
        "billable_hours": round(
            billable_seconds / 3600,
            2,
        ),
        "estimated_earnings": estimated_earnings,
    }


def get_timesheet_report(
    user,
    start_date=None,
    end_date=None,
    project_id=None,
    client_id=None,
    billable=None,
    ordering="-start_time",
):
    """
    Return completed time entries with optional filters.
    """

    entries = (
        get_completed_entries(user)
        .select_related(
            "project",
            "project__client",
            "task",
        )
    )

    if start_date:
        entries = entries.filter(
            start_time__date__gte=start_date,
        )

    if end_date:
        entries = entries.filter(
            start_time__date__lte=end_date,
        )

    if project_id:
        entries = entries.filter(
            project_id=project_id,
        )

    if client_id:
        entries = entries.filter(
            project__client_id=client_id,
        )

    if billable is not None:
        entries = entries.filter(
            billable=billable,
        )

    allowed_ordering = {
        "start_time",
        "-start_time",
        "hourly_rate",
        "-hourly_rate",
    }

    if ordering not in allowed_ordering:
        ordering = "-start_time"

    return entries.order_by(
        ordering,
    )


def get_daily_report(
    *,
    user,
):
    """
    Return today's report for the authenticated user.
    """

    today = timezone.localdate()

    entries = (
        TimeEntry.objects.filter(
            owner=user,
            status=TimeEntryStatus.COMPLETED,
            start_time__date=today,
        )
        .select_related(
            "project",
            "task",
        )
        .order_by("start_time")
    )

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
            total_earnings += entry.earnings
        else:
            non_billable_hours += hours

    return {
        "date": today,
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
        "entries": entries,
    }


def get_weekly_report(
    *,
    user,
):
    """
    Return this week's report for the authenticated user.
    """

    today = timezone.localdate()

    week_start = today - timedelta(
        days=today.weekday()
    )

    week_end = week_start + timedelta(
        days=6
    )

    entries = (
        TimeEntry.objects.filter(
            owner=user,
            status=TimeEntryStatus.COMPLETED,
            start_time__date__gte=week_start,
            start_time__date__lte=week_end,
        )
        .select_related(
            "project",
            "task",
        )
        .order_by("start_time")
    )

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
            total_earnings += entry.earnings
        else:
            non_billable_hours += hours

    return {
        "week_start": week_start,
        "week_end": week_end,
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
        "entries": entries,
    }


def get_monthly_report(
    *,
    user,
):
    """
    Return the current month's report.
    """

    today = timezone.localdate()

    entries = (
        TimeEntry.objects.filter(
            owner=user,
            status=TimeEntryStatus.COMPLETED,
            start_time__year=today.year,
            start_time__month=today.month,
        )
        .select_related(
            "project",
            "task",
        )
        .order_by("start_time")
    )

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
            total_earnings += entry.earnings
        else:
            non_billable_hours += hours

    return {
        "month": month_name[today.month],
        "year": today.year,
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
        "entries": entries,
    }


def get_project_report(
    *,
    user,
    project_id,
):
    """
    Return a report for a single project.
    """

    project = get_object_or_404(
        Project,
        id=project_id,
        owner=user,
    )

    entries = (
        TimeEntry.objects.filter(
            owner=user,
            project=project,
            status=TimeEntryStatus.COMPLETED,
        )
        .select_related(
            "project",
            "task",
        )
        .order_by("start_time")
    )

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
            total_earnings += entry.earnings
        else:
            non_billable_hours += hours

    return {
        "project": project,
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
        "entries": entries,
    }


def get_client_report(
    *,
    user,
    client_id,
):
    """
    Return report for a specific client.
    """

    entries = (
        TimeEntry.objects.filter(
            owner=user,
            status=TimeEntryStatus.COMPLETED,
            project__client_id=client_id,
        )
        .select_related(
            "project",
            "project__client",
            "task",
        )
        .order_by("start_time")
    )

    if not entries.exists():
        return None

    client = entries.first().project.client

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
            total_earnings += entry.earnings
        else:
            non_billable_hours += hours

    return {
        "client": client,
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
        "entries": entries,
    }


def get_dashboard_analytics(
    *,
    user,
):
    """
    Return dashboard analytics for the authenticated user.
    """

    today = timezone.localdate()

    week_start = today - timedelta(
        days=today.weekday(),
    )

    completed_entries = (
        get_completed_entries(
            user,
        )
        .select_related(
            "project",
            "project__client",
        )
    )

    total_entries = completed_entries.count()

    today_hours = Decimal("0.00")
    week_hours = Decimal("0.00")
    month_hours = Decimal("0.00")
    billable_hours = Decimal("0.00")
    non_billable_hours = Decimal("0.00")
    estimated_earnings = Decimal("0.00")

    for entry in completed_entries:

        if not entry.duration:
            continue

        hours = Decimal(
            str(
                entry.duration.total_seconds() / 3600
            )
        )

        if entry.start_time.date() == today:
            today_hours += hours

        if entry.start_time.date() >= week_start:
            week_hours += hours

        if (
            entry.start_time.year == today.year
            and entry.start_time.month == today.month
        ):
            month_hours += hours

        if entry.billable:
            billable_hours += hours
        else:
            non_billable_hours += hours

        estimated_earnings += entry.earnings

    active_projects = (
        completed_entries
        .values("project")
        .distinct()
        .count()
    )

    completed_projects = (
        completed_entries
        .filter(
            project__status="completed",
        )
        .values("project")
        .distinct()
        .count()
    )

    top_project = (
        completed_entries
        .values(
            "project__id",
            "project__name",
        )
        .annotate(
            total_duration=Sum(
                "duration",
            )
        )
        .order_by(
            "-total_duration",
        )
        .first()
    )

    top_client = (
        completed_entries
        .values(
            "project__client__id",
            "project__client__name",
        )
        .annotate(
            total_duration=Sum(
                "duration",
            )
        )
        .order_by(
            "-total_duration",
        )
        .first()
    )

    return {
        "today_hours": today_hours.quantize(
            Decimal("0.01")
        ),
        "week_hours": week_hours.quantize(
            Decimal("0.01")
        ),
        "month_hours": month_hours.quantize(
            Decimal("0.01")
        ),
        "completed_entries": total_entries,
        "billable_hours": billable_hours.quantize(
            Decimal("0.01")
        ),
        "non_billable_hours": non_billable_hours.quantize(
            Decimal("0.01")
        ),
        "estimated_earnings": estimated_earnings.quantize(
            Decimal("0.01")
        ),
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "top_project": top_project,
        "top_client": top_client,
    }


def get_productivity_analytics(
    *,
    user,
):
    """
    Return the last 7 days of productivity.
    """

    today = timezone.localdate()

    start_date = today - timedelta(
        days=6
    )

    entries = (
        get_completed_entries(
            user,
        )
        .filter(
            start_time__date__gte=start_date,
        )
        .order_by("start_time")
    )

    daily_hours = defaultdict(Decimal)

    for entry in entries:

        if not entry.duration:
            continue

        hours = Decimal(
            str(
                entry.duration.total_seconds() / 3600
            )
        )

        day = entry.start_time.date()

        daily_hours[day] += hours

    results = []

    for i in range(7):

        current_day = start_date + timedelta(
            days=i
        )

        results.append(
            {
                "date": current_day,
                "hours": daily_hours[
                    current_day
                ].quantize(
                    Decimal("0.01")
                ),
            }
        )

    return results


def get_team_report(
    *,
    user,
):
    """
    Return team reporting data for projects
    managed by the authenticated user.

    The manager can only see completed time entries
    belonging to projects where they are the owner.
    """

    projects = (
        Project.objects.filter(
            owner=user,
        )
        .select_related(
            "client",
        )
        .prefetch_related(
            "members",
        )
        .order_by(
            "name",
        )
    )

    entries = (
        TimeEntry.objects.filter(
            project__owner=user,
            status=TimeEntryStatus.COMPLETED,
        )
        .select_related(
            "owner",
            "project",
            "project__client",
            "task",
        )
        .order_by(
            "-start_time",
        )
    )

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
            total_earnings += entry.earnings

        else:

            non_billable_hours += hours

    # ------------------------------------------------------
    # Team members
    # ------------------------------------------------------

    members = {}

    for project in projects:

        for member in project.members.all():

            if member.id not in members:

                members[member.id] = {
                    "id": member.id,
                    "username": member.username,
                    "first_name": member.first_name,
                    "last_name": member.last_name,
                    "total_entries": 0,
                    "total_hours": Decimal("0.00"),
                    "billable_hours": Decimal("0.00"),
                    "non_billable_hours": Decimal("0.00"),
                    "estimated_earnings": Decimal("0.00"),
                }

    for entry in entries:

        member_id = entry.owner_id

        if member_id not in members:
            continue

        member = members[member_id]

        member["total_entries"] += 1

        if not entry.duration:
            continue

        hours = Decimal(
            str(
                entry.duration.total_seconds() / 3600
            )
        )

        member["total_hours"] += hours

        if entry.billable:

            member["billable_hours"] += hours
            member["estimated_earnings"] += (
                entry.earnings
            )

        else:

            member["non_billable_hours"] += hours

    team_members = []

    for member in members.values():

        team_members.append(
            {
                **member,
                "total_hours": member[
                    "total_hours"
                ].quantize(
                    Decimal("0.01")
                ),
                "billable_hours": member[
                    "billable_hours"
                ].quantize(
                    Decimal("0.01")
                ),
                "non_billable_hours": member[
                    "non_billable_hours"
                ].quantize(
                    Decimal("0.01")
                ),
                "estimated_earnings": member[
                    "estimated_earnings"
                ].quantize(
                    Decimal("0.01")
                ),
            }
        )

    team_members.sort(
        key=lambda member: (
            -float(member["total_hours"]),
            member["username"],
        )
    )

    # ------------------------------------------------------
    # Project statistics
    # ------------------------------------------------------

    project_stats = {}

    for project in projects:

        project_stats[project.id] = {
            "id": project.id,
            "name": project.name,
            "client": project.client.name,
            "status": project.status,
            "total_entries": 0,
            "total_hours": Decimal("0.00"),
            "billable_hours": Decimal("0.00"),
            "non_billable_hours": Decimal("0.00"),
            "estimated_earnings": Decimal("0.00"),
        }

    for entry in entries:

        project_id = entry.project_id

        if project_id not in project_stats:
            continue

        project = project_stats[project_id]

        project["total_entries"] += 1

        if not entry.duration:
            continue

        hours = Decimal(
            str(
                entry.duration.total_seconds() / 3600
            )
        )

        project["total_hours"] += hours

        if entry.billable:

            project["billable_hours"] += hours
            project["estimated_earnings"] += (
                entry.earnings
            )

        else:

            project["non_billable_hours"] += hours

    project_results = []

    for project in project_stats.values():

        project_results.append(
            {
                **project,
                "total_hours": project[
                    "total_hours"
                ].quantize(
                    Decimal("0.01")
                ),
                "billable_hours": project[
                    "billable_hours"
                ].quantize(
                    Decimal("0.01")
                ),
                "non_billable_hours": project[
                    "non_billable_hours"
                ].quantize(
                    Decimal("0.01")
                ),
                "estimated_earnings": project[
                    "estimated_earnings"
                ].quantize(
                    Decimal("0.01")
                ),
            }
        )

    project_results.sort(
        key=lambda project: (
            -float(project["total_hours"]),
            project["name"],
        )
    )

    return {
        "total_projects": projects.count(),
        "total_members": len(team_members),
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
        "estimated_earnings": total_earnings.quantize(
            Decimal("0.01")
        ),
        "projects": project_results,
        "team_members": team_members,
        "recent_entries": entries[:10],
    }
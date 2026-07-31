from decimal import Decimal
from datetime import timedelta

from django.utils import timezone

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

    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

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

from calendar import month_name


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
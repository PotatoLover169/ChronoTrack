from decimal import Decimal

from apps.tracker.models import (
    TimeEntry,
    TimeEntryStatus,
)


def get_report_summary(user):
    """
    Generate a summary report for the authenticated user.
    """

    completed_entries = TimeEntry.objects.filter(
        owner=user,
        status=TimeEntryStatus.COMPLETED,
    )

    total_entries = completed_entries.count()

    billable_entries = completed_entries.filter(
        billable=True,
    ).count()

    non_billable_entries = completed_entries.filter(
        billable=False,
    ).count()

    total_seconds = 0
    billable_seconds = 0

    estimated_earnings = Decimal("0.00")

    for entry in completed_entries:

        if entry.duration:
            seconds = entry.duration.total_seconds()

            total_seconds += seconds

            if entry.billable:
                billable_seconds += seconds

        estimated_earnings += entry.earnings

    total_hours = round(
        total_seconds / 3600,
        2,
    )

    billable_hours = round(
        billable_seconds / 3600,
        2,
    )

    return {
        "total_entries": total_entries,
        "completed_entries": total_entries,
        "billable_entries": billable_entries,
        "non_billable_entries": non_billable_entries,
        "total_duration_hours": total_hours,
        "billable_hours": billable_hours,
        "estimated_earnings": estimated_earnings,
    }
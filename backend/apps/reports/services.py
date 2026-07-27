from decimal import Decimal

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
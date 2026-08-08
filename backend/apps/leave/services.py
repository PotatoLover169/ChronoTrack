from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .exceptions import (
    InsufficientLeaveBalanceError,
    InvalidLeaveDatesError,
    LeaveRequestAlreadyReviewedError,
    LeaveRequestPermissionError,
    PendingLeaveRequestExistsError,
)
from .models import (
    LeaveBalance,
    LeaveRequest,
    LeaveRequestStatus,
)


def calculate_leave_days(
    start_date: date,
    end_date: date,
) -> Decimal:
    """
    Calculate the number of leave days between two dates.

    Both the start date and end date are included.

    Example:
        August 10 -> August 10 = 1 day
        August 10 -> August 12 = 3 days
    """

    if end_date < start_date:
        raise InvalidLeaveDatesError(
            "End date cannot be earlier than start date."
        )

    return Decimal(
        (end_date - start_date).days + 1
    )


@transaction.atomic
def create_leave_request(
    *,
    employee,
    leave_type,
    start_date,
    end_date,
    reason,
):
    """
    Create a new leave request for an employee.

    The request is created as PENDING.

    Leave balance is NOT deducted here.
    Balance deduction happens only after approval.
    """

    if not reason or not reason.strip():
        raise InvalidLeaveDatesError(
            "Leave request reason is required."
        )

    if not leave_type.is_active:
        raise InvalidLeaveDatesError(
            "This leave type is currently inactive."
        )

    days = calculate_leave_days(
        start_date,
        end_date,
    )

    # Prevent overlapping pending leave requests.
    overlapping_request = LeaveRequest.objects.filter(
        employee=employee,
        status=LeaveRequestStatus.PENDING,
        start_date__lte=end_date,
        end_date__gte=start_date,
    ).exists()

    if overlapping_request:
        raise PendingLeaveRequestExistsError(
            "You already have a pending leave request "
            "that overlaps with these dates."
        )

    # For now, keep a leave request within one calendar year.
    # This matches the LeaveBalance model, which is year-specific.
    if start_date.year != end_date.year:
        raise InvalidLeaveDatesError(
            "Leave requests cannot currently span multiple calendar years."
        )

    balance = (
        LeaveBalance.objects
        .select_for_update()
        .filter(
            employee=employee,
            leave_type=leave_type,
            year=start_date.year,
        )
        .first()
    )

    if balance is None:
        raise InsufficientLeaveBalanceError(
            "No leave balance has been allocated for "
            f"{leave_type.name} in {start_date.year}."
        )

    # Include already-pending requests when checking availability.
    # This prevents an employee from submitting multiple pending
    # requests that collectively exceed their available balance.
    pending_days = (
        LeaveRequest.objects
        .filter(
            employee=employee,
            leave_type=leave_type,
            status=LeaveRequestStatus.PENDING,
            start_date__year=start_date.year,
        )
        .exclude(
            start_date__gt=end_date,
            end_date__lt=start_date,
        )
    )

    pending_days_total = Decimal("0")

    for request in pending_days:
        pending_days_total += request.days

    available_days = (
        balance.allocated_days
        - balance.used_days
        - pending_days_total
    )

    if days > available_days:
        raise InsufficientLeaveBalanceError(
            f"Insufficient {leave_type.name} leave balance. "
            f"Available days: {available_days}."
        )

    leave_request = LeaveRequest.objects.create(
        employee=employee,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        days=days,
        reason=reason.strip(),
        status=LeaveRequestStatus.PENDING,
    )

    return leave_request
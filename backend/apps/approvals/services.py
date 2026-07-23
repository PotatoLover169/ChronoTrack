from django.db import transaction

from .exceptions import PendingEditRequestExistsError
from .models import (
    EditRequestStatus,
    TimeEntryEditRequest,
)


@transaction.atomic
def create_edit_request(
    *,
    user,
    time_entry,
    requested_project=None,
    requested_task=None,
    requested_start_time=None,
    requested_end_time=None,
    requested_description="",
    requested_billable=True,
    reason,
    proof_screenshot=None,
):
    """
    Create a new Time Entry Edit Request.
    """

    existing_request = TimeEntryEditRequest.objects.filter(
        time_entry=time_entry,
        status=EditRequestStatus.PENDING,
    ).first()

    if existing_request:
        raise PendingEditRequestExistsError(
            "A pending edit request already exists for this time entry."
        )

    edit_request = TimeEntryEditRequest.objects.create(
        time_entry=time_entry,
        requested_by=user,
        requested_project=requested_project,
        requested_task=requested_task,
        requested_start_time=requested_start_time,
        requested_end_time=requested_end_time,
        requested_description=requested_description,
        requested_billable=requested_billable,
        reason=reason,
        proof_screenshot=proof_screenshot,
        status=EditRequestStatus.PENDING,
    )

    return edit_request
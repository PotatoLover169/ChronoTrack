from django.db import transaction
from django.utils import timezone

from .exceptions import (
    EditRequestAlreadyReviewedError,
    PendingEditRequestExistsError,
)
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


@transaction.atomic
def approve_edit_request(
    *,
    edit_request,
    manager,
    manager_comment="",
):
    """
    Approve a Time Entry Edit Request.
    """

    if edit_request.status != EditRequestStatus.PENDING:
        raise EditRequestAlreadyReviewedError(
            "This edit request has already been reviewed."
        )

    time_entry = edit_request.time_entry

    if edit_request.requested_project is not None:
        time_entry.project = edit_request.requested_project

    if edit_request.requested_task is not None:
        time_entry.task = edit_request.requested_task

    if edit_request.requested_start_time is not None:
        time_entry.start_time = edit_request.requested_start_time

    if edit_request.requested_end_time is not None:
        time_entry.end_time = edit_request.requested_end_time

    time_entry.description = edit_request.requested_description
    time_entry.billable = edit_request.requested_billable

    time_entry.save()

    edit_request.status = EditRequestStatus.APPROVED
    edit_request.reviewed_by = manager
    edit_request.reviewed_at = timezone.now()
    edit_request.manager_comment = manager_comment

    edit_request.save()

    return edit_request

from django.utils import timezone


@transaction.atomic
def reject_edit_request(
    *,
    manager,
    edit_request,
    manager_comment,
):
    """
    Reject a pending edit request.
    """

    if edit_request.status != EditRequestStatus.PENDING:
        raise ValueError(
            "Only pending edit requests can be rejected."
        )

    if not manager_comment.strip():
        raise ValueError(
            "Manager comment is required."
        )

    edit_request.status = EditRequestStatus.REJECTED
    edit_request.reviewed_by = manager
    edit_request.reviewed_at = timezone.now()
    edit_request.manager_comment = manager_comment

    edit_request.save(
        update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
            "manager_comment",
        ]
    )

    return edit_request
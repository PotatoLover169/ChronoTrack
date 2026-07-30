from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework import serializers
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.approvals.permissions import (
    IsEmployee,
    IsManagerOrAdmin,
)

from apps.approvals.exceptions import (
    EditRequestAlreadyReviewedError,
    PendingEditRequestExistsError,
)

from apps.approvals.models import (
    EditRequestStatus,
    TimeEntryEditRequest,
)

from apps.approvals.services import (
    approve_edit_request,
    create_edit_request,
    reject_edit_request,
)

from .serializers import (
    ManagerCommentSerializer,
    TimeEntryEditRequestSerializer,
    TimeEntryEditRequestDetailSerializer,
)


class CreateTimeEntryEditRequestView(
    generics.CreateAPIView,
):
    """
    Employee submits an edit request.
    """

    serializer_class = (
        TimeEntryEditRequestSerializer
    )

    permission_classes = (
        IsAuthenticated,
        IsEmployee,
    )

    def perform_create(
        self,
        serializer,
    ):
        data = serializer.validated_data

        try:
            edit_request = create_edit_request(
                user=self.request.user,
                time_entry=data["time_entry"],
                requested_project=data.get(
                    "requested_project"
                ),
                requested_task=data.get(
                    "requested_task"
                ),
                requested_start_time=data.get(
                    "requested_start_time"
                ),
                requested_end_time=data.get(
                    "requested_end_time"
                ),
                requested_description=data.get(
                    "requested_description",
                    "",
                ),
                requested_billable=data.get(
                    "requested_billable",
                    True,
                ),
                reason=data["reason"],
                proof_screenshot=data.get(
                    "proof_screenshot",
                ),
            )

        except PendingEditRequestExistsError as exc:
            raise serializers.ValidationError(
                {
                    "detail": str(exc),
                }
            )

        serializer.instance = edit_request


class MyTimeEntryEditRequestListView(
    generics.ListAPIView,
):
    """
    Employee views only his own requests.
    """

    serializer_class = (
        TimeEntryEditRequestDetailSerializer
    )

    permission_classes = (
        IsAuthenticated,
        IsEmployee,
    )

    def get_queryset(self):
        return (
            TimeEntryEditRequest.objects.filter(
                requested_by=self.request.user,
            )
            .select_related(
                "time_entry",
                "requested_project",
                "requested_task",
                "reviewed_by",
            )
            .order_by("-requested_at")
        )


class CancelTimeEntryEditRequestView(
    generics.GenericAPIView,
):
    """
    Employee cancels his own pending request.
    """

    permission_classes = (
        IsAuthenticated,
        IsEmployee,
    )

    def patch(
        self,
        request,
        pk,
    ):
        edit_request = get_object_or_404(
            TimeEntryEditRequest,
            pk=pk,
            requested_by=request.user,
        )

        if edit_request.status != EditRequestStatus.PENDING:
            return Response(
                {
                    "detail": (
                        "Only pending requests can be cancelled."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        edit_request.status = (
            EditRequestStatus.CANCELLED
        )

        edit_request.save(
            update_fields=[
                "status",
            ]
        )

        return Response(
            {
                "message": (
                    "Edit request cancelled successfully."
                )
            },
            status=status.HTTP_200_OK,
        )


class PendingTimeEntryEditRequestListView(
    generics.ListAPIView,
):
    """
    Manager/Admin views pending requests.
    """

    serializer_class = (
        TimeEntryEditRequestDetailSerializer
    )

    permission_classes = (
        IsAuthenticated,
        IsManagerOrAdmin,
    )

    def get_queryset(self):
        return (
            TimeEntryEditRequest.objects.filter(
                status=EditRequestStatus.PENDING,
            )
            .select_related(
                "time_entry",
                "requested_by",
                "reviewed_by",
                "requested_project",
                "requested_task",
            )
            .order_by("-requested_at")
        )


class TimeEntryEditRequestDetailView(
    generics.RetrieveAPIView,
):
    """
    Manager/Admin views one request.
    """

    serializer_class = (
        TimeEntryEditRequestDetailSerializer
    )

    permission_classes = (
        IsAuthenticated,
        IsManagerOrAdmin,
    )

    def get_queryset(self):
        return (
            TimeEntryEditRequest.objects.select_related(
                "time_entry",
                "requested_by",
                "reviewed_by",
                "requested_project",
                "requested_task",
            )
        )


class ApproveTimeEntryEditRequestView(
    generics.GenericAPIView,
):
    """
    Manager/Admin approves a request.
    """

    serializer_class = (
        ManagerCommentSerializer
    )

    permission_classes = (
        IsAuthenticated,
        IsManagerOrAdmin,
    )

    def get_queryset(self):
        return (
            TimeEntryEditRequest.objects.select_related(
                "time_entry",
            )
        )

    def patch(
        self,
        request,
        pk,
    ):
        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        edit_request = get_object_or_404(
            self.get_queryset(),
            pk=pk,
        )

        try:
            approve_edit_request(
                edit_request=edit_request,
                manager=request.user,
                manager_comment=serializer.validated_data[
                    "manager_comment"
                ],
            )

        except (
            EditRequestAlreadyReviewedError,
            ValueError,
        ) as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {
                "message": (
                    "Time entry edit request approved successfully."
                ),
            },
            status=status.HTTP_200_OK,
        )


class RejectTimeEntryEditRequestView(
    generics.GenericAPIView,
):
    """
    Manager/Admin rejects a request.
    """

    serializer_class = (
        ManagerCommentSerializer
    )

    permission_classes = (
        IsAuthenticated,
        IsManagerOrAdmin,
    )

    def get_queryset(self):
        return (
            TimeEntryEditRequest.objects.select_related(
                "time_entry",
            )
        )

    def patch(
        self,
        request,
        pk,
    ):
        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        edit_request = get_object_or_404(
            self.get_queryset(),
            pk=pk,
        )

        try:
            reject_edit_request(
                manager=request.user,
                edit_request=edit_request,
                manager_comment=serializer.validated_data[
                    "manager_comment"
                ],
            )

        except (
            EditRequestAlreadyReviewedError,
            ValueError,
        ) as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {
                "message": (
                    "Time entry edit request rejected successfully."
                ),
            },
            status=status.HTTP_200_OK,
        )
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.approvals.exceptions import (
    EditRequestAlreadyReviewedError,
)
from apps.approvals.models import (
    EditRequestStatus,
    TimeEntryEditRequest,
)
from apps.approvals.services import (
    approve_edit_request,
)

from .serializers import (
    ApproveTimeEntryEditRequestSerializer,
    TimeEntryEditRequestDetailSerializer,
)


class PendingTimeEntryEditRequestListView(generics.ListAPIView):
    """
    List all pending Time Entry Edit Requests.
    """

    serializer_class = (
        TimeEntryEditRequestDetailSerializer
    )

    permission_classes = (
        IsAuthenticated,
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


class TimeEntryEditRequestDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single Time Entry Edit Request.
    """

    serializer_class = (
        TimeEntryEditRequestDetailSerializer
    )

    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        return (
            TimeEntryEditRequest.objects
            .select_related(
                "time_entry",
                "requested_by",
                "reviewed_by",
                "requested_project",
                "requested_task",
            )
        )


class ApproveTimeEntryEditRequestView(generics.GenericAPIView):
    """
    Approve a Time Entry Edit Request.
    """

    serializer_class = (
        ApproveTimeEntryEditRequestSerializer
    )

    permission_classes = (
        IsAuthenticated,
    )

    def patch(self, request, pk):
        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        edit_request = generics.get_object_or_404(
            TimeEntryEditRequest,
            pk=pk,
        )

        try:
            approve_edit_request(
                edit_request=edit_request,
                manager=request.user,
                manager_comment=serializer.validated_data.get(
                    "manager_comment",
                    "",
                ),
            )

        except EditRequestAlreadyReviewedError as exc:
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
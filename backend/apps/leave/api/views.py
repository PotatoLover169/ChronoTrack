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


from apps.leave.exceptions import (
    InsufficientLeaveBalanceError,
    LeaveRequestAlreadyReviewedError,
)


from apps.leave.models import (
    LeaveBalance,
    LeaveRequest,
    LeaveRequestStatus,
    LeaveType,
)


from apps.leave.services import (
    approve_leave_request,
    cancel_leave_request,
    create_leave_request,
    reject_leave_request,
)


from .serializers import (
    CreateLeaveRequestSerializer,
    LeaveBalanceSerializer,
    LeaveRequestSerializer,
    LeaveTypeSerializer,
    ManagerCommentSerializer,
    ManageLeaveBalanceSerializer,
)


# ======================================================
# Leave Types
# ======================================================

class LeaveTypeListView(
    generics.ListAPIView,
):
    """
    Return all active leave types.
    """

    serializer_class = LeaveTypeSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        return LeaveType.objects.filter(
            is_active=True,
        ).order_by(
            "name",
        )


# ======================================================
# Employee Leave Balances
# ======================================================

class MyLeaveBalanceListView(
    generics.ListAPIView,
):
    """
    Return the authenticated employee's
    leave balances.
    """

    serializer_class = LeaveBalanceSerializer

    permission_classes = (
        IsAuthenticated,
        IsEmployee,
    )

    def get_queryset(self):
        return (
            LeaveBalance.objects.filter(
                employee=self.request.user,
            )
            .select_related(
                "leave_type",
            )
            .order_by(
                "-year",
                "leave_type__name",
            )
        )

class ManageLeaveBalanceListView(
    generics.ListAPIView,
):
    """
    Manager/Admin views employee leave balances.
    """

    serializer_class = ManageLeaveBalanceSerializer

    permission_classes = (
        IsAuthenticated,
        IsManagerOrAdmin,
    )

    def get_queryset(self):
        queryset = (
            LeaveBalance.objects
            .select_related(
                "employee",
                "leave_type",
            )
            .order_by(
                "employee_id",
                "leave_type__name",
                "-year",
            )
        )

        employee_id = self.request.query_params.get(
            "employee",
        )

        leave_type_id = self.request.query_params.get(
            "leave_type",
        )

        year = self.request.query_params.get(
            "year",
        )

        if employee_id:
            queryset = queryset.filter(
                employee_id=employee_id,
            )

        if leave_type_id:
            queryset = queryset.filter(
                leave_type_id=leave_type_id,
            )

        if year:
            queryset = queryset.filter(
                year=year,
            )

        return queryset

# ============================================================
# CREATE LEAVE REQUEST
# ============================================================

class CreateLeaveRequestView(
    generics.CreateAPIView,
):
    """
    Employee submits a leave request.
    """

    serializer_class = (
        CreateLeaveRequestSerializer
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
            leave_request = create_leave_request(
                employee=self.request.user,
                leave_type=data["leave_type"],
                start_date=data["start_date"],
                end_date=data["end_date"],
                reason=data["reason"],
            )

        except InsufficientLeaveBalanceError as exc:
            raise serializers.ValidationError(
                {
                    "detail": str(exc),
                }
            )

        except ValueError as exc:
            raise serializers.ValidationError(
                {
                    "detail": str(exc),
                }
            )

        serializer.instance = leave_request


class MyLeaveRequestListView(
    generics.ListAPIView,
):
    """
    Employee views only their own leave requests.
    """

    serializer_class = LeaveRequestSerializer

    permission_classes = (
        IsAuthenticated,
        IsEmployee,
    )

    def get_queryset(self):
        return (
            LeaveRequest.objects.filter(
                employee=self.request.user,
            )
            .select_related(
                "leave_type",
                "reviewed_by",
            )
            .order_by(
                "-requested_at",
            )
        )

class MyLeaveRequestDetailView(
    generics.RetrieveAPIView,
):
    """
    Employee views one of their own leave requests.
    """

    serializer_class = LeaveRequestSerializer

    permission_classes = (
        IsAuthenticated,
        IsEmployee,
    )

    def get_queryset(self):
        return (
            LeaveRequest.objects.filter(
                employee=self.request.user,
            )
            .select_related(
                "leave_type",
                "reviewed_by",
            )
        )

class CancelLeaveRequestView(
    generics.GenericAPIView,
):
    """
    Employee cancels their own pending request.
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
        leave_request = get_object_or_404(
            LeaveRequest,
            pk=pk,
            employee=request.user,
        )

        try:
            cancel_leave_request(
                user=request.user,
                leave_request=leave_request,
            )

        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": (
                    "Leave request cancelled successfully."
                ),
            },
            status=status.HTTP_200_OK,
        )


# ======================================================
# Manager / Admin Leave Requests
# ======================================================

class PendingLeaveRequestListView(
    generics.ListAPIView,
):
    """
    Manager/Admin views pending leave requests.
    """

    serializer_class = LeaveRequestSerializer

    permission_classes = (
        IsAuthenticated,
        IsManagerOrAdmin,
    )

    def get_queryset(self):
        queryset = (
            LeaveRequest.objects.filter(
                status=LeaveRequestStatus.PENDING,
            )
            .select_related(
                "employee",
                "leave_type",
                "reviewed_by",
            )
            .order_by(
                "-requested_at",
            )
        )

        employee_id = self.request.query_params.get(
            "employee",
        )

        leave_type_id = self.request.query_params.get(
            "leave_type",
        )

        if employee_id:
            queryset = queryset.filter(
                employee_id=employee_id,
            )

        if leave_type_id:
            queryset = queryset.filter(
                leave_type_id=leave_type_id,
            )

        return queryset


class LeaveRequestDetailView(
    generics.RetrieveAPIView,
):
    """
    Manager/Admin views a single leave request.
    """

    serializer_class = LeaveRequestSerializer

    permission_classes = (
        IsAuthenticated,
        IsManagerOrAdmin,
    )

    def get_queryset(self):
        return (
            LeaveRequest.objects.select_related(
                "employee",
                "leave_type",
                "reviewed_by",
            )
        )


class ApproveLeaveRequestView(
    generics.GenericAPIView,
):
    """
    Manager/Admin approves a leave request.
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
            LeaveRequest.objects.select_related(
                "employee",
                "leave_type",
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

        leave_request = get_object_or_404(
            self.get_queryset(),
            pk=pk,
        )

        try:
            approve_leave_request(
                leave_request=leave_request,
                manager=request.user,
                manager_comment=serializer.validated_data.get(
                    "manager_comment",
                    "",
                ),
            )

        except (
            LeaveRequestAlreadyReviewedError,
            InsufficientLeaveBalanceError,
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
                    "Leave request approved successfully."
                ),
            },
            status=status.HTTP_200_OK,
        )

class RejectLeaveRequestView(
    generics.GenericAPIView,
):
    """
    Manager/Admin rejects a pending leave request.
    """

    serializer_class = ManagerCommentSerializer

    permission_classes = (
        IsAuthenticated,
        IsManagerOrAdmin,
    )

    def get_queryset(self):
        return (
            LeaveRequest.objects.select_related(
                "employee",
                "leave_type",
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

        leave_request = get_object_or_404(
            self.get_queryset(),
            pk=pk,
        )

        try:
            reject_leave_request(
                leave_request=leave_request,
                manager=request.user,
                manager_comment=serializer.validated_data.get(
                    "manager_comment",
                    "",
                ),
            )

        except LeaveRequestAlreadyReviewedError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_409_CONFLICT,
            )

        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": (
                    "Leave request rejected successfully."
                ),
            },
            status=status.HTTP_200_OK,
        )
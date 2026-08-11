from rest_framework import serializers

from apps.leave.models import (
    LeaveBalance,
    LeaveRequest,
    LeaveType,
)


class LeaveTypeSerializer(
    serializers.ModelSerializer,
):
    class Meta:
        model = LeaveType

        fields = (
            "id",
            "name",
            "description",
            "default_days",
            "is_paid",
            "is_active",
        )

        read_only_fields = (
            "id",
        )


class LeaveBalanceSerializer(
    serializers.ModelSerializer,
):
    remaining_days = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )

    leave_type = LeaveTypeSerializer(
        read_only=True,
    )

    class Meta:
        model = LeaveBalance

        fields = (
            "id",
            "leave_type",
            "year",
            "allocated_days",
            "used_days",
            "remaining_days",
        )

        read_only_fields = fields

class ManageLeaveBalanceSerializer(
    serializers.ModelSerializer,
):
    employee = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    remaining_days = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True,
    )

    leave_type = LeaveTypeSerializer(
        read_only=True,
    )

    class Meta:
        model = LeaveBalance

        fields = (
            "id",
            "employee",
            "leave_type",
            "year",
            "allocated_days",
            "used_days",
            "remaining_days",
        )

        read_only_fields = fields

class UpdateLeaveBalanceSerializer(
    serializers.ModelSerializer,
):
    class Meta:
        model = LeaveBalance

        fields = (
            "allocated_days",
        )

    def validate_allocated_days(
        self,
        value,
    ):
        if value < 0:
            raise serializers.ValidationError(
                "Allocated days cannot be negative."
            )

        return value

class CreateLeaveRequestSerializer(
    serializers.ModelSerializer,
):
    leave_type = serializers.PrimaryKeyRelatedField(
        queryset=LeaveType.objects.filter(
            is_active=True,
        ),
    )

    class Meta:
        model = LeaveRequest

        fields = (
            "id",
            "leave_type",
            "start_date",
            "end_date",
            "reason",
        )

        read_only_fields = (
            "id",
        )


class LeaveRequestSerializer(
    serializers.ModelSerializer,
):
    leave_type = LeaveTypeSerializer(
        read_only=True,
    )

    class Meta:
        model = LeaveRequest

        fields = (
            "id",
            "employee",
            "leave_type",
            "start_date",
            "end_date",
            "days",
            "reason",
            "status",
            "reviewed_by",
            "manager_comment",
            "requested_at",
            "reviewed_at",
            "cancelled_at",
        )

        read_only_fields = fields


class ManagerCommentSerializer(
    serializers.Serializer,
):
    manager_comment = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
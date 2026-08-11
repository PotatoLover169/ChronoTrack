from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class LeaveType(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    default_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )

    is_paid = models.BooleanField(
        default=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = (
            "name",
        )

        verbose_name = "Leave Type"

        verbose_name_plural = (
            "Leave Types"
        )

    def __str__(self):
        return self.name


class LeaveBalance(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave_balances",
    )

    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name="balances",
    )

    year = models.PositiveIntegerField()

    allocated_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )

    used_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = (
            "-year",
            "employee",
            "leave_type",
        )

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "employee",
                    "leave_type",
                    "year",
                ],
                name="unique_employee_leave_balance_per_year",
            ),
        ]

        verbose_name = "Leave Balance"

        verbose_name_plural = (
            "Leave Balances"
        )

    def __str__(self):
        return (
            f"{self.employee} - "
            f"{self.leave_type.name} - "
            f"{self.year}"
        )

    @property
    def remaining_days(self):
        return (
            self.allocated_days
            - self.used_days
        )

class LeaveRequestStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class LeaveRequest(models.Model):
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )

    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT,
        related_name="requests",
    )

    start_date = models.DateField()

    end_date = models.DateField()

    days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=LeaveRequestStatus.choices,
        default=LeaveRequestStatus.PENDING,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_leave_requests",
    )

    manager_comment = models.TextField(
        blank=True,
    )

    requested_at = models.DateTimeField(
        auto_now_add=True,
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = (
            "-requested_at",
        )

        verbose_name = "Leave Request"

        verbose_name_plural = "Leave Requests"

    def __str__(self):
        return (
            f"Leave Request #{self.pk} - "
            f"{self.employee} - "
            f"{self.leave_type.name}"
        )

class LeaveSettlement(models.Model):
    """
    Records the year-end conversion of unused leave
    into salary.
    """

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="leave_settlements",
    )

    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT,
        related_name="settlements",
    )

    year = models.PositiveIntegerField()

    allocated_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    used_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    unused_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    daily_salary_rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    converted_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="processed_leave_settlements",
    )

    processed_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = (
            "-year",
            "employee",
            "leave_type",
        )

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "employee",
                    "leave_type",
                    "year",
                ],
                name="unique_leave_settlement_per_year",
            ),
        ]

        verbose_name = "Leave Settlement"

        verbose_name_plural = (
            "Leave Settlements"
        )

    def __str__(self):
        return (
            f"{self.employee} - "
            f"{self.leave_type.name} - "
            f"{self.year}"
        )
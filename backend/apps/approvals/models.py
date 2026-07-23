from django.conf import settings
from django.db import models


class EditRequestStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class TimeEntryEditRequest(models.Model):
    time_entry = models.ForeignKey(
        "tracker.TimeEntry",
        on_delete=models.CASCADE,
        related_name="edit_requests",
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="time_entry_edit_requests",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_time_entry_requests",
    )

    requested_project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="time_entry_edit_requests",
    )

    requested_task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="time_entry_edit_requests",
    )

    requested_start_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    requested_end_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    requested_description = models.TextField(
        blank=True,
    )

    requested_billable = models.BooleanField(
        default=True,
    )

    reason = models.TextField()

    proof_screenshot = models.ImageField(
        upload_to="time_entry_edit_requests/",
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=EditRequestStatus.choices,
        default=EditRequestStatus.PENDING,
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

    class Meta:
        ordering = (
            "-requested_at",
        )

        verbose_name = "Time Entry Edit Request"

        verbose_name_plural = (
            "Time Entry Edit Requests"
        )

    def __str__(self):
        return (
            f"Edit Request #{self.pk} "
            f"for Time Entry #{self.time_entry_id}"
        )
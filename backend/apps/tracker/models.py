from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.projects.models import Project
from apps.tasks.models import Task


class TimeEntryStatus(models.TextChoices):
    RUNNING = "running", "Running"
    PAUSED = "paused", "Paused"
    COMPLETED = "completed", "Completed"


class TimeEntry(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="time_entries",
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="time_entries",
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="time_entries",
    )

    description = models.TextField(
        blank=True,
    )

    start_time = models.DateTimeField()

    end_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    duration = models.DurationField(
        null=True,
        blank=True,
    )

    billable = models.BooleanField(
        default=True,
    )

    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=TimeEntryStatus.choices,
        default=TimeEntryStatus.RUNNING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-start_time"]

    def clean(self):
        """
        Ensure the selected task belongs to the selected project.
        """
        if self.task and self.task.project != self.project:
            raise ValidationError(
                {
                    "task": "The selected task does not belong to the selected project."
                }
            )

    def save(self, *args, **kwargs):
        """
        Automatically snapshots the project's hourly rate and
        calculates the duration when the timer is completed.
        """

        # Snapshot the project's hourly rate only once.
        if not self.hourly_rate:
            self.hourly_rate = self.project.hourly_rate

        # Calculate duration when both timestamps exist.
        if self.start_time and self.end_time:
            self.duration = self.end_time - self.start_time

        # Run model validation before saving.
        self.full_clean()

        super().save(*args, **kwargs)

    @property
    def earnings(self):
        """
        Calculates the billable earnings for this time entry.
        """

        if not self.billable or not self.duration:
            return Decimal("0.00")

        hours = Decimal(
            str(self.duration.total_seconds() / 3600)
        )

        return (
            hours * self.hourly_rate
        ).quantize(
            Decimal("0.01")
        )

    def __str__(self):
        return f"{self.project.name} - {self.owner.username}"
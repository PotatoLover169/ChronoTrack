from django.conf import settings
from django.db import models

from apps.clients.models import Client


class Project(models.Model):
    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("in_progress", "In Progress"),
        ("on_hold", "On Hold"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="projects",
    )

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planning",
    )

    start_date = models.DateField(
        null=True,
        blank=True,
    )

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
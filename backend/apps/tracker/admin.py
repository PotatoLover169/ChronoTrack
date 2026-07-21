from django.contrib import admin

from .models import TimeEntry


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "project",
        "task",
        "status",
        "duration",
        "billable",
        "start_time",
    )

    list_filter = (
        "status",
        "billable",
        "project",
    )

    search_fields = (
        "owner__username",
        "project__name",
        "task__title",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "duration",
        "hourly_rate",
    )

    ordering = (
        "-start_time",
    )
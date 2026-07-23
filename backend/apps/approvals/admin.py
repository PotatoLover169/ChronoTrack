from django.contrib import admin

from .models import TimeEntryEditRequest


@admin.register(TimeEntryEditRequest)
class TimeEntryEditRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "time_entry",
        "requested_by",
        "status",
        "requested_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "reason",
        "requested_by__username",
    )

    readonly_fields = (
        "requested_at",
        "reviewed_at",
    )
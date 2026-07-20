from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "priority",
        "status",
        "completed",
        "owner",
    )

    list_filter = (
        "priority",
        "status",
        "completed",
    )

    search_fields = (
        "title",
        "project__name",
    )
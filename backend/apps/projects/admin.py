from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "client",
        "status",
        "owner",
        "start_date",
        "end_date",
    )

    list_filter = (
        "status",
        "client",
    )

    search_fields = (
        "name",
        "client__name",
    )
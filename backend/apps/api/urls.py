from django.urls import include, path

urlpatterns = [
    # Authentication API
    path("auth/", include("apps.accounts.api.urls")),

    # Dashboard API
    path("dashboard/", include("apps.dashboard.api.urls")),

    # Client API
    path("clients/", include("apps.clients.api.urls")),

    # Projects API
    path("projects/", include("apps.projects.api.urls")),

    # Tasks API
    path("tasks/", include("apps.tasks.api.urls")),

    # Tracker API
    path("tracker/", include("apps.tracker.api.urls")),

    # Reports API
    path("reports/", include("apps.reports.api.urls")),

    # Approvals API
    path("approvals/", include("apps.approvals.api.urls")),

    # Notifications API
    path("notifications/", include("apps.notifications.api.urls")),

    # Leave API
    path("leave/", include("apps.leave.api.urls")),
]
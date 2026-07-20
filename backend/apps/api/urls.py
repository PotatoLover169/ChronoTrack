from django.urls import include, path

urlpatterns = [
    # Dashboard API
    path("dashboard/", include("apps.dashboard.api.urls")),

    # Authentication API
    path("auth/", include("apps.accounts.api.urls")),

    # Client API
    path("clients/", include("apps.clients.api.urls")),

    # Projects API
    path("projects/", include("apps.projects.api.urls")),

    # Tasks API
    path("tasks/", include("apps.tasks.api.urls")),
]
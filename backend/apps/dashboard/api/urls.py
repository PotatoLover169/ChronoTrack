from django.urls import path

from .views import (
    DashboardAPIView,
    DashboardRecentEntriesAPIView,
    HealthCheckAPIView,
)

urlpatterns = [
    path(
        "",
        DashboardAPIView.as_view(),
        name="dashboard",
    ),

    path(
        "recent-entries/",
        DashboardRecentEntriesAPIView.as_view(),
        name="dashboard-recent-entries",
    ),

    path(
        "health/",
        HealthCheckAPIView.as_view(),
        name="health-check",
    ),
]
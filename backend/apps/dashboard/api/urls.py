from django.urls import path

from .views import (
    DashboardAPIView,
    DashboardRecentEntriesAPIView,
    HealthCheckAPIView,
    DashboardRecentProjectsAPIView,
    DashboardUpcomingTasksAPIView,
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
    
    path(
        "recent-projects/",
        DashboardRecentProjectsAPIView.as_view(),
        name="dashboard-recent-projects",
        ),
        
    path(
        "upcoming-tasks/",
        DashboardUpcomingTasksAPIView.as_view(),
        name="dashboard-upcoming-tasks",
        ),
]
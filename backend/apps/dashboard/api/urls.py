from django.urls import path

from .views import (
    DashboardAPIView,
    DashboardRecentEntriesAPIView,
    HealthCheckAPIView,
    DashboardRecentProjectsAPIView,
    DashboardUpcomingTasksAPIView,
    DashboardOverdueTasksAPIView,
    DashboardActiveTimerAPIView,
    DashboardQuickStatsAPIView,
    DashboardFeedAPIView,
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

    path(
        "overdue-tasks/",
        DashboardOverdueTasksAPIView.as_view(),
        name="dashboard-overdue-tasks",
        ),

    path(
        "active-timer/",
        DashboardActiveTimerAPIView.as_view(),
        name="dashboard-active-timer",
        ),

    path(
        "quick-stats/",
        DashboardQuickStatsAPIView.as_view(),
        name="dashboard-quick-stats",
        ),

    path(
        "feed/",
        DashboardFeedAPIView.as_view(),
        name="dashboard-feed",
        ),
]
from django.urls import path

from .views import (
    CurrentTimerView,
    StartTimerView,
    StopTimerView,
    TimeEntryDetailView,
    TimeEntryListView,
)

urlpatterns = [
    path(
        "",
        TimeEntryListView.as_view(),
        name="time-entry-list",
    ),
    path(
        "<int:pk>/",
        TimeEntryDetailView.as_view(),
        name="time-entry-detail",
    ),
    path(
        "start/",
        StartTimerView.as_view(),
        name="start-timer",
    ),
    path(
        "stop/",
        StopTimerView.as_view(),
        name="stop-timer",
    ),
    path(
        "current/",
        CurrentTimerView.as_view(),
        name="current-timer",
    ),
]
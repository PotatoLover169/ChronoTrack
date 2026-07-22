from django.urls import path

from .views import (
    CurrentTimerView,
    StartTimerView,
    StopTimerView,
)

urlpatterns = [
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
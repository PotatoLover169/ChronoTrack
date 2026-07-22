from django.urls import path

from .views import (
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
]
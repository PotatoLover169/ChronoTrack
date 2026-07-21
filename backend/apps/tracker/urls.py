from django.urls import path

from .views import StartTimerView

urlpatterns = [
    path(
        "start/",
        StartTimerView.as_view(),
        name="start-timer",
    ),
]
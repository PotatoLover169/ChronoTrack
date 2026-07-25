from django.urls import path

from .views import (
    DashboardAPIView,
    HealthCheckAPIView,
)

urlpatterns = [
    path(
        "",
        DashboardAPIView.as_view(),
        name="dashboard",
    ),

    path(
        "health/",
        HealthCheckAPIView.as_view(),
        name="health-check",
    ),
]
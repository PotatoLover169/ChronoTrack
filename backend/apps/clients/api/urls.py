from django.urls import path

from .views import (
    ClientListCreateAPIView,
    ClientRetrieveUpdateDestroyAPIView,
    ClientDashboardAPIView,
)

urlpatterns = [
    path(
        "",
        ClientListCreateAPIView.as_view(),
        name="client-list-create",
    ),
    path(
        "<int:pk>/",
        ClientRetrieveUpdateDestroyAPIView.as_view(),
        name="client-detail",
    ),
    path(
        "<int:pk>/dashboard/",
        ClientDashboardAPIView.as_view(),
        name="client-dashboard",
    ),
]
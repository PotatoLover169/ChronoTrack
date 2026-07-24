from django.urls import path

from .views import (
    ApproveTimeEntryEditRequestView,
    PendingTimeEntryEditRequestListView,
    TimeEntryEditRequestDetailView,
)

urlpatterns = [
    path(
        "time-entry-edit-requests/",
        PendingTimeEntryEditRequestListView.as_view(),
        name="pending-time-entry-edit-requests",
    ),

    path(
        "time-entry-edit-requests/<int:pk>/",
        TimeEntryEditRequestDetailView.as_view(),
        name="time-entry-edit-request-detail",
    ),

    path(
        "time-entry-edit-requests/<int:pk>/approve/",
        ApproveTimeEntryEditRequestView.as_view(),
        name="approve-time-entry-edit-request",
    ),
]
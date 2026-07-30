from django.urls import path

from .views import (
    ApproveTimeEntryEditRequestView,
    CancelTimeEntryEditRequestView,
    CreateTimeEntryEditRequestView,
    MyTimeEntryEditRequestListView,
    PendingTimeEntryEditRequestListView,
    RejectTimeEntryEditRequestView,
    TimeEntryEditRequestDetailView,
)

urlpatterns = [
    # ==========================
    # Employee Endpoints
    # ==========================

    path(
        "time-entry-edit-requests/create/",
        CreateTimeEntryEditRequestView.as_view(),
        name="create-time-entry-edit-request",
    ),

    path(
        "time-entry-edit-requests/my/",
        MyTimeEntryEditRequestListView.as_view(),
        name="my-time-entry-edit-requests",
    ),

    path(
        "time-entry-edit-requests/<int:pk>/cancel/",
        CancelTimeEntryEditRequestView.as_view(),
        name="cancel-time-entry-edit-request",
    ),

    # ==========================
    # Manager / Admin Endpoints
    # ==========================

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

    path(
        "time-entry-edit-requests/<int:pk>/reject/",
        RejectTimeEntryEditRequestView.as_view(),
        name="reject-time-entry-edit-request",
    ),
]
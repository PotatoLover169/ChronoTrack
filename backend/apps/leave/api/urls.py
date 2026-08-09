from django.urls import path

from .views import (
    ApproveLeaveRequestView,
    CancelLeaveRequestView,
    CreateLeaveRequestView,
    LeaveRequestDetailView,
    LeaveTypeListView,
    MyLeaveBalanceListView,
    MyLeaveRequestListView,
    PendingLeaveRequestListView,
    RejectLeaveRequestView,
)


urlpatterns = [
    # ==================================================
    # Leave Types
    # ==================================================

    path(
        "types/",
        LeaveTypeListView.as_view(),
        name="leave-type-list",
    ),

    # ==================================================
    # Employee Endpoints
    # ==================================================

    path(
        "balances/",
        MyLeaveBalanceListView.as_view(),
        name="my-leave-balances",
    ),

    path(
        "requests/create/",
        CreateLeaveRequestView.as_view(),
        name="create-leave-request",
    ),

    path(
        "requests/my/",
        MyLeaveRequestListView.as_view(),
        name="my-leave-requests",
    ),

    path(
        "requests/<int:pk>/cancel/",
        CancelLeaveRequestView.as_view(),
        name="cancel-leave-request",
    ),

    # ==================================================
    # Manager / Admin Endpoints
    # ==================================================

    path(
        "requests/",
        PendingLeaveRequestListView.as_view(),
        name="pending-leave-requests",
    ),

    path(
        "requests/<int:pk>/",
        LeaveRequestDetailView.as_view(),
        name="leave-request-detail",
    ),

    path(
        "requests/<int:pk>/approve/",
        ApproveLeaveRequestView.as_view(),
        name="approve-leave-request",
    ),

    path(
        "requests/<int:pk>/reject/",
        RejectLeaveRequestView.as_view(),
        name="reject-leave-request",
    ),
]
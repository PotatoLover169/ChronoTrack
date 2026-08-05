from django.urls import path

from .views import (
    NotificationDeleteAPIView,
    NotificationListAPIView,
    UnreadNotificationListAPIView,
    MarkNotificationReadAPIView,
    MarkAllNotificationsReadAPIView,
)

urlpatterns = [
    path(
        "",
        NotificationListAPIView.as_view(),
        name="notification-list",
    ),

    path(
        "unread/",
        UnreadNotificationListAPIView.as_view(),
        name="notification-unread",
    ),

    path(
        "<int:pk>/read/",
        MarkNotificationReadAPIView.as_view(),
        name="notification-read",
    ),

    path(
        "read-all/",
        MarkAllNotificationsReadAPIView.as_view(),
        name="notification-read-all",
    ),

    path(
        "<int:pk>/",
        NotificationDeleteAPIView.as_view(),
        name="notification-delete",
    ),
]
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import Notification
from apps.notifications.services import (
    get_notifications,
    get_unread_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read,
)

from .serializers import NotificationSerializer


class NotificationListAPIView(
    generics.ListAPIView,
):
    """
    Return all notifications.
    """

    permission_classes = (
        IsAuthenticated,
    )

    serializer_class = NotificationSerializer

    def get_queryset(self):
        return get_notifications(
            self.request.user,
        )


class UnreadNotificationListAPIView(
    generics.ListAPIView,
):
    """
    Return unread notifications.
    """

    permission_classes = (
        IsAuthenticated,
    )

    serializer_class = NotificationSerializer

    def get_queryset(self):
        return get_unread_notifications(
            self.request.user,
        )


class MarkNotificationReadAPIView(
    APIView,
):
    """
    Mark a notification as read.
    """

    permission_classes = (
        IsAuthenticated,
    )

    def patch(
        self,
        request,
        pk,
    ):
        notification = generics.get_object_or_404(
            Notification,
            pk=pk,
            recipient=request.user,
        )

        mark_notification_as_read(
            notification,
        )

        return Response(
            {
                "message": "Notification marked as read.",
            },
            status=status.HTTP_200_OK,
        )


class MarkAllNotificationsReadAPIView(
    APIView,
):
    """
    Mark all notifications as read.
    """

    permission_classes = (
        IsAuthenticated,
    )

    def patch(
        self,
        request,
    ):
        count = mark_all_notifications_as_read(
            request.user,
        )

        return Response(
            {
                "message": f"{count} notification(s) marked as read.",
            },
            status=status.HTTP_200_OK,
        )


class NotificationDeleteAPIView(
    generics.DestroyAPIView,
):
    """
    Delete a notification.
    """

    permission_classes = (
        IsAuthenticated,
    )

    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user,
        )
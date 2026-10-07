from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.notifications.models import Notification


User = get_user_model()


class NotificationAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="employee",
            email="employee@example.com",
            password="password123",
        )

        self.other_user = User.objects.create_user(
            username="other_employee",
            email="other@example.com",
            password="password123",
        )

        self.list_url = reverse(
            "notification-list"
        )

        self.unread_url = reverse(
            "notification-unread"
        )

        self.read_all_url = reverse(
            "notification-read-all"
        )

    def create_notification(
        self,
        recipient,
        title="Test Notification",
        is_read=False,
    ):
        return Notification.objects.create(
            recipient=recipient,
            notification_type="system",
            title=title,
            message=f"{title} message.",
            is_read=is_read,
        )

    # =====================================================
    # LIST
    # =====================================================

    def test_authenticated_user_can_list_notifications(
        self,
    ):
        self.create_notification(
            recipient=self.user,
            title="My Notification",
        )

        self.create_notification(
            recipient=self.other_user,
            title="Other Notification",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["title"],
            "My Notification",
        )

    def test_user_cannot_see_other_users_notifications(
        self,
    ):
        self.create_notification(
            recipient=self.other_user,
            title="Private Notification",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            0,
        )

    # =====================================================
    # UNREAD
    # =====================================================

    def test_authenticated_user_can_list_unread_notifications(
        self,
    ):
        self.create_notification(
            recipient=self.user,
            title="Unread",
            is_read=False,
        )

        self.create_notification(
            recipient=self.user,
            title="Read",
            is_read=True,
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.unread_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["title"],
            "Unread",
        )

    # =====================================================
    # MARK ONE AS READ
    # =====================================================

    def test_user_can_mark_own_notification_as_read(
        self,
    ):
        notification = self.create_notification(
            recipient=self.user,
            title="Unread Notification",
        )

        url = reverse(
            "notification-read",
            kwargs={
                "pk": notification.pk
            },
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["message"],
            "Notification marked as read.",
        )

        notification.refresh_from_db()

        self.assertTrue(
            notification.is_read
        )

    def test_user_cannot_mark_other_users_notification_as_read(
        self,
    ):
        notification = self.create_notification(
            recipient=self.other_user,
            title="Private Notification",
        )

        url = reverse(
            "notification-read",
            kwargs={
                "pk": notification.pk
            },
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        notification.refresh_from_db()

        self.assertFalse(
            notification.is_read
        )

    # =====================================================
    # MARK ALL AS READ
    # =====================================================

    def test_user_can_mark_all_own_notifications_as_read(
        self,
    ):
        first = self.create_notification(
            recipient=self.user,
            title="First",
        )

        second = self.create_notification(
            recipient=self.user,
            title="Second",
        )

        other = self.create_notification(
            recipient=self.other_user,
            title="Other",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            self.read_all_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["message"],
            "2 notification(s) marked as read.",
        )

        first.refresh_from_db()
        second.refresh_from_db()
        other.refresh_from_db()

        self.assertTrue(
            first.is_read
        )

        self.assertTrue(
            second.is_read
        )

        self.assertFalse(
            other.is_read
        )

    def test_mark_all_returns_zero_when_no_unread_notifications(
        self,
    ):
        self.create_notification(
            recipient=self.user,
            title="Already Read",
            is_read=True,
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            self.read_all_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["message"],
            "0 notification(s) marked as read.",
        )

    # =====================================================
    # DELETE
    # =====================================================

    def test_user_can_delete_own_notification(
        self,
    ):
        notification = self.create_notification(
            recipient=self.user,
            title="Delete Me",
        )

        url = reverse(
            "notification-delete",
            kwargs={
                "pk": notification.pk
            },
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.delete(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Notification.objects.filter(
                pk=notification.pk
            ).exists()
        )

    def test_user_cannot_delete_other_users_notification(
        self,
    ):
        notification = self.create_notification(
            recipient=self.other_user,
            title="Private Notification",
        )

        url = reverse(
            "notification-delete",
            kwargs={
                "pk": notification.pk
            },
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.delete(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            Notification.objects.filter(
                pk=notification.pk
            ).exists()
        )

    # =====================================================
    # AUTHENTICATION
    # =====================================================

    def test_unauthenticated_user_cannot_list_notifications(
        self,
    ):
        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unauthenticated_user_cannot_list_unread_notifications(
        self,
    ):
        response = self.client.get(
            self.unread_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unauthenticated_user_cannot_mark_all_as_read(
        self,
    ):
        response = self.client.patch(
            self.read_all_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # =====================================================
    # SERIALIZED FIELDS
    # =====================================================

    def test_notification_response_does_not_expose_recipient(
        self,
    ):
        self.create_notification(
            recipient=self.user,
            title="Private",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        notification_data = response.data[0]

        self.assertNotIn(
            "recipient",
            notification_data,
        )

        self.assertIn(
            "id",
            notification_data,
        )

        self.assertIn(
            "notification_type",
            notification_data,
        )

        self.assertIn(
            "title",
            notification_data,
        )

        self.assertIn(
            "message",
            notification_data,
        )

        self.assertIn(
            "is_read",
            notification_data,
        )

        self.assertIn(
            "created_at",
            notification_data,
        )
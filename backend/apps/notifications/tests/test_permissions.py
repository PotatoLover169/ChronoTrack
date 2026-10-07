from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.notifications.models import Notification


User = get_user_model()


class NotificationPermissionsTestCase(APITestCase):

    def setUp(self):
        self.employee = User.objects.create_user(
            username="employee",
            email="employee@example.com",
            password="password123",
        )

        self.manager = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="password123",
        )

        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password123",
        )

        self.employee_notification = (
            Notification.objects.create(
                recipient=self.employee,
                notification_type="system",
                title="Employee Notification",
                message="Employee notification.",
            )
        )

        self.manager_notification = (
            Notification.objects.create(
                recipient=self.manager,
                notification_type="system",
                title="Manager Notification",
                message="Manager notification.",
            )
        )

    # =====================================================
    # EMPLOYEE
    # =====================================================

    def test_employee_can_access_own_notifications(
        self,
    ):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            reverse("notification-list")
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
            "Employee Notification",
        )

    def test_employee_cannot_access_manager_notification(
        self,
    ):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            reverse("notification-list")
        )

        titles = [
            notification["title"]
            for notification in response.data
        ]

        self.assertNotIn(
            "Manager Notification",
            titles,
        )

    # =====================================================
    # MANAGER
    # =====================================================

    def test_manager_can_access_own_notifications(
        self,
    ):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.get(
            reverse("notification-list")
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
            "Manager Notification",
        )

    def test_manager_cannot_access_employee_notification(
        self,
    ):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.get(
            reverse("notification-list")
        )

        titles = [
            notification["title"]
            for notification in response.data
        ]

        self.assertNotIn(
            "Employee Notification",
            titles,
        )

    # =====================================================
    # ADMIN
    # =====================================================

    def test_admin_still_only_sees_own_notifications(
        self,
    ):
        admin_notification = Notification.objects.create(
            recipient=self.admin,
            notification_type="system",
            title="Admin Notification",
            message="Admin notification.",
        )

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            reverse("notification-list")
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
            response.data[0]["id"],
            admin_notification.id,
        )

    # =====================================================
    # OBJECT OWNERSHIP
    # =====================================================

    def test_employee_cannot_mark_manager_notification_as_read(
        self,
    ):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.patch(
            reverse(
                "notification-read",
                kwargs={
                    "pk": self.manager_notification.pk
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_employee_cannot_delete_manager_notification(
        self,
    ):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.delete(
            reverse(
                "notification-delete",
                kwargs={
                    "pk": self.manager_notification.pk
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            Notification.objects.filter(
                pk=self.manager_notification.pk
            ).exists()
        )

    # =====================================================
    # UNAUTHENTICATED
    # =====================================================

    def test_unauthenticated_user_is_denied(
        self,
    ):
        response = self.client.get(
            reverse("notification-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unauthenticated_user_cannot_delete(
        self,
    ):
        response = self.client.delete(
            reverse(
                "notification-delete",
                kwargs={
                    "pk": self.employee_notification.pk
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
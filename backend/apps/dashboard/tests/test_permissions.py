from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework.test import APIClient


User = get_user_model()


class DashboardPermissionsTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="dashboard_permission_user",
            email="permission@example.com",
            password="TestPassword123!",
        )

    def test_dashboard_requires_authentication(self):
        endpoints = [
            "/api/dashboard/",
            "/api/dashboard/recent-entries/",
            "/api/dashboard/recent-projects/",
            "/api/dashboard/upcoming-tasks/",
            "/api/dashboard/overdue-tasks/",
            "/api/dashboard/active-timer/",
            "/api/dashboard/quick-stats/",
            "/api/dashboard/feed/",
        ]

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(
                    endpoint
                )

                self.assertEqual(
                    response.status_code,
                    401,
                )

    def test_authenticated_user_can_access_dashboard(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            "/api/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_authenticated_user_can_access_dashboard_sub_endpoints(
        self,
    ):
        self.client.force_authenticate(
            user=self.user
        )

        endpoints = [
            "/api/dashboard/recent-entries/",
            "/api/dashboard/recent-projects/",
            "/api/dashboard/upcoming-tasks/",
            "/api/dashboard/overdue-tasks/",
            "/api/dashboard/active-timer/",
            "/api/dashboard/quick-stats/",
            "/api/dashboard/feed/",
        ]

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(
                    endpoint
                )

                self.assertEqual(
                    response.status_code,
                    200,
                )

    def test_health_endpoint_does_not_require_authentication(
        self,
    ):
        response = self.client.get(
            "/api/dashboard/health/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )
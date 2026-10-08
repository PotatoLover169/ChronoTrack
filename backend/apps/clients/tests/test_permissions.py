from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from rest_framework.test import APIClient

from apps.clients.models import Client
from apps.projects.models import Project


User = get_user_model()


class ClientPermissionsTestCase(TestCase):

    def setUp(self):
        self.api_client = APIClient()

        self.employee = User.objects.create_user(
            username="employee_permission",
            email="employee_permission@example.com",
            password="TestPassword123!",
        )

        self.manager = User.objects.create_user(
            username="manager_permission",
            email="manager_permission@example.com",
            password="TestPassword123!",
        )

        self.admin = User.objects.create_user(
            username="admin_permission",
            email="admin_permission@example.com",
            password="TestPassword123!",
        )

        manager_group, _ = Group.objects.get_or_create(
            name="Manager"
        )

        admin_group, _ = Group.objects.get_or_create(
            name="Admin"
        )

        self.manager.groups.add(
            manager_group
        )

        self.admin.groups.add(
            admin_group
        )

        self.client = Client.objects.create(
            owner=self.employee,
            name="Permission Client",
            company="Permission Company",
        )

        self.unrelated_client = Client.objects.create(
            owner=self.manager,
            name="Unrelated Client",
        )

        self.project = Project.objects.create(
            owner=self.employee,
            client=self.client,
            name="Permission Project",
            status="in_progress",
        )

    # ---------------------------------------------------------
    # AUTHENTICATION
    # ---------------------------------------------------------

    def test_client_list_requires_authentication(self):
        response = self.api_client.get(
            "/api/clients/"
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_client_detail_requires_authentication(self):
        response = self.api_client.get(
            f"/api/clients/{self.client.id}/"
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_client_dashboard_requires_authentication(self):
        response = self.api_client.get(
            f"/api/clients/{self.client.id}/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    # ---------------------------------------------------------
    # EMPLOYEE
    # ---------------------------------------------------------

    def test_employee_has_read_access(self):
        self.api_client.force_authenticate(
            user=self.employee
        )

        response = self.api_client.get(
            "/api/clients/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_employee_cannot_create(self):
        self.api_client.force_authenticate(
            user=self.employee
        )

        response = self.api_client.post(
            "/api/clients/",
            {
                "name": "Unauthorized Client",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_employee_cannot_update(self):
        self.api_client.force_authenticate(
            user=self.employee
        )

        response = self.api_client.patch(
            f"/api/clients/{self.client.id}/",
            {
                "name": "Unauthorized Update",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_employee_cannot_delete(self):
        self.api_client.force_authenticate(
            user=self.employee
        )

        response = self.api_client.delete(
            f"/api/clients/{self.client.id}/"
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    # ---------------------------------------------------------
    # MANAGER
    # ---------------------------------------------------------

    def test_manager_can_create(self):
        self.api_client.force_authenticate(
            user=self.manager
        )

        response = self.api_client.post(
            "/api/clients/",
            {
                "name": "Manager Permission Client",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_manager_can_update(self):
        self.api_client.force_authenticate(
            user=self.manager
        )

        response = self.api_client.patch(
            f"/api/clients/{self.client.id}/",
            {
                "name": "Manager Updated Permission Client",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_manager_can_delete(self):
        self.api_client.force_authenticate(
            user=self.manager
        )

        response = self.api_client.delete(
            f"/api/clients/{self.client.id}/"
        )

        self.assertEqual(
            response.status_code,
            204,
        )

    # ---------------------------------------------------------
    # ADMIN
    # ---------------------------------------------------------

    def test_admin_can_create(self):
        self.api_client.force_authenticate(
            user=self.admin
        )

        response = self.api_client.post(
            "/api/clients/",
            {
                "name": "Admin Permission Client",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_admin_can_update(self):
        self.api_client.force_authenticate(
            user=self.admin
        )

        response = self.api_client.patch(
            f"/api/clients/{self.client.id}/",
            {
                "name": "Admin Updated Permission Client",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_admin_can_delete(self):
        self.api_client.force_authenticate(
            user=self.admin
        )

        response = self.api_client.delete(
            f"/api/clients/{self.client.id}/"
        )

        self.assertEqual(
            response.status_code,
            204,
        )
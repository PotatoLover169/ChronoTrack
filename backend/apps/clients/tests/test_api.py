from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIClient

from apps.clients.models import Client
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.tracker.models import (
    TimeEntry,
    TimeEntryStatus,
)


User = get_user_model()


class ClientAPITestCase(TestCase):

    def setUp(self):
        self.api_client = APIClient()

        self.employee = User.objects.create_user(
            username="employee_api",
            email="employee_api@example.com",
            password="TestPassword123!",
        )

        self.other_employee = User.objects.create_user(
            username="other_employee_api",
            email="other_api@example.com",
            password="TestPassword123!",
        )

        self.manager = User.objects.create_user(
            username="manager_api",
            email="manager_api@example.com",
            password="TestPassword123!",
        )

        self.admin = User.objects.create_user(
            username="admin_api",
            email="admin_api@example.com",
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
            name="API Client",
            company="API Company",
            email="api@example.com",
            phone="09170000000",
            notes="API client notes",
        )

        self.other_client = Client.objects.create(
            owner=self.other_employee,
            name="Other API Client",
        )

        self.employee_project = Project.objects.create(
            owner=self.employee,
            client=self.client,
            name="Employee API Project",
            status="in_progress",
            hourly_rate=Decimal("100.00"),
        )

        self.other_project = Project.objects.create(
            owner=self.other_employee,
            client=self.other_client,
            name="Other API Project",
            status="in_progress",
            hourly_rate=Decimal("150.00"),
        )

        self.employee_project.members.add(
            self.employee
        )

    def authenticate(self, user):
        self.api_client.force_authenticate(
            user=user
        )

    # ---------------------------------------------------------
    # LIST
    # ---------------------------------------------------------

    def test_employee_can_list_accessible_clients(self):
        self.authenticate(
            self.employee
        )

        response = self.api_client.get(
            "/api/clients/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        names = [
            item["name"]
            for item in response.data
        ]

        self.assertIn(
            "API Client",
            names,
        )

        self.assertNotIn(
            "Other API Client",
            names,
        )

    def test_manager_can_list_all_clients(self):
        self.authenticate(
            self.manager
        )

        response = self.api_client.get(
            "/api/clients/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        names = [
            item["name"]
            for item in response.data
        ]

        self.assertIn(
            "API Client",
            names,
        )

        self.assertIn(
            "Other API Client",
            names,
        )

    def test_admin_can_list_all_clients(self):
        self.authenticate(
            self.admin
        )

        response = self.api_client.get(
            "/api/clients/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    def test_employee_cannot_create_client(self):
        self.authenticate(
            self.employee
        )

        response = self.api_client.post(
            "/api/clients/",
            {
                "name": "Employee Created Client",
                "company": "Employee Company",
                "email": "new@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertFalse(
            Client.objects.filter(
                name="Employee Created Client"
            ).exists()
        )

    def test_manager_can_create_client(self):
        self.authenticate(
            self.manager
        )

        response = self.api_client.post(
            "/api/clients/",
            {
                "name": "Manager Created Client",
                "company": "Manager Company",
                "email": "manager_client@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        client = Client.objects.get(
            name="Manager Created Client"
        )

        self.assertEqual(
            client.owner,
            self.manager,
        )

    def test_admin_can_create_client(self):
        self.authenticate(
            self.admin
        )

        response = self.api_client.post(
            "/api/clients/",
            {
                "name": "Admin Created Client",
                "company": "Admin Company",
                "email": "admin_client@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        client = Client.objects.get(
            name="Admin Created Client"
        )

        self.assertEqual(
            client.owner,
            self.admin,
        )

    # ---------------------------------------------------------
    # DETAIL
    # ---------------------------------------------------------

    def test_employee_can_retrieve_accessible_client(self):
        self.authenticate(
            self.employee
        )

        response = self.api_client.get(
            f"/api/clients/{self.client.id}/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["name"],
            "API Client",
        )

    def test_employee_cannot_retrieve_inaccessible_client(self):
        self.authenticate(
            self.employee
        )

        response = self.api_client.get(
            f"/api/clients/{self.other_client.id}/"
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_manager_can_retrieve_any_client(self):
        self.authenticate(
            self.manager
        )

        response = self.api_client.get(
            f"/api/clients/{self.other_client.id}/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def test_employee_cannot_update_client(self):
        self.authenticate(
            self.employee
        )

        response = self.api_client.patch(
            f"/api/clients/{self.client.id}/",
            {
                "name": "Employee Updated Client",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.client.refresh_from_db()

        self.assertEqual(
            self.client.name,
            "API Client",
        )

    def test_manager_can_update_client(self):
        self.authenticate(
            self.manager
        )

        response = self.api_client.patch(
            f"/api/clients/{self.client.id}/",
            {
                "name": "Manager Updated Client",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.client.refresh_from_db()

        self.assertEqual(
            self.client.name,
            "Manager Updated Client",
        )

    def test_admin_can_update_client(self):
        self.authenticate(
            self.admin
        )

        response = self.api_client.patch(
            f"/api/clients/{self.client.id}/",
            {
                "name": "Admin Updated Client",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.client.refresh_from_db()

        self.assertEqual(
            self.client.name,
            "Admin Updated Client",
        )

    # ---------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------

    def test_employee_cannot_delete_client(self):
        self.authenticate(
            self.employee
        )

        response = self.api_client.delete(
            f"/api/clients/{self.client.id}/"
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertTrue(
            Client.objects.filter(
                id=self.client.id
            ).exists()
        )

    def test_manager_can_delete_client(self):
        self.authenticate(
            self.manager
        )

        response = self.api_client.delete(
            f"/api/clients/{self.client.id}/"
        )

        self.assertEqual(
            response.status_code,
            204,
        )

        self.assertFalse(
            Client.objects.filter(
                id=self.client.id
            ).exists()
        )

    # ---------------------------------------------------------
    # DASHBOARD
    # ---------------------------------------------------------

    def test_employee_can_access_client_dashboard(self):
        self.authenticate(
            self.employee
        )

        TimeEntry.objects.create(
            owner=self.employee,
            project=self.employee_project,
            description="Dashboard API entry",
            start_time=timezone.now()
            - timedelta(hours=2),
            end_time=timezone.now(),
            billable=True,
            status=TimeEntryStatus.COMPLETED,
        )

        response = self.api_client.get(
            f"/api/clients/{self.client.id}/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["client"]["id"],
            self.client.id,
        )

        self.assertEqual(
            response.data["total_projects"],
            1,
        )

        self.assertEqual(
            response.data["total_entries"],
            1,
        )

        self.assertEqual(
            response.data["total_hours"],
            "2.00",
        )

        self.assertEqual(
            response.data["billable_hours"],
            "2.00",
        )

    def test_employee_cannot_access_inaccessible_dashboard(self):
        self.authenticate(
            self.employee
        )

        response = self.api_client.get(
            f"/api/clients/{self.other_client.id}/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_manager_can_access_any_dashboard(self):
        self.authenticate(
            self.manager
        )

        response = self.api_client.get(
            f"/api/clients/{self.other_client.id}/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_admin_can_access_any_dashboard(self):
        self.authenticate(
            self.admin
        )

        response = self.api_client.get(
            f"/api/clients/{self.client.id}/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )
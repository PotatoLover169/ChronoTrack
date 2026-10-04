from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.clients.models import Client
from apps.projects.models import Project
from apps.tracker.models import TimeEntry, TimeEntryStatus


User = get_user_model()


class ReportsPermissionTestCase(APITestCase):

    def setUp(self):
        self.employee = User.objects.create_user(
            username="employee",
            email="employee@example.com",
            password="TestPass123!",
        )

        self.manager = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="TestPass123!",
        )

        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="TestPass123!",
        )

        manager_group, _ = Group.objects.get_or_create(
            name="Manager",
        )

        self.manager.groups.add(manager_group)

        self.client_record = Client.objects.create(
            owner=self.manager,
            name="Permission Client",
            company="Permission Company",
        )

        self.project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Permission Project",
            description="Permission project",
            status="in_progress",
            hourly_rate=500,
        )

        self.project.members.add(
            self.employee,
        )

        self.entry = TimeEntry.objects.create(
            owner=self.employee,
            project=self.project,
            description="Permission entry",
            start_time=timezone.now()
            - timedelta(hours=2),
            end_time=timezone.now()
            - timedelta(hours=1),
            billable=True,
            status=TimeEntryStatus.COMPLETED,
        )

    # --------------------------------------------------
    # PERSONAL REPORTS
    # --------------------------------------------------

    def test_employee_can_access_personal_reports(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        endpoints = [
            "/api/reports/summary/",
            "/api/reports/me/daily/",
            "/api/reports/me/weekly/",
            "/api/reports/me/monthly/",
            "/api/reports/timesheet/",
            "/api/reports/dashboard/",
            "/api/reports/dashboard/productivity/",
        ]

        for endpoint in endpoints:
            response = self.client.get(endpoint)

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                endpoint,
            )

    def test_manager_can_access_personal_reports(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            "/api/reports/summary/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_admin_can_access_personal_reports(self):
        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.get(
            "/api/reports/summary/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # TEAM REPORT
    # --------------------------------------------------

    def test_employee_is_denied_team_report(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            "/api/reports/team/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_manager_is_allowed_team_report(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            "/api/reports/team/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_admin_is_allowed_team_report(self):
        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.get(
            "/api/reports/team/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # ORGANIZATION REPORT
    # --------------------------------------------------

    def test_employee_is_denied_organization_report(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            "/api/reports/organization/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_manager_is_denied_organization_report(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            "/api/reports/organization/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_admin_is_allowed_organization_report(self):
        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.get(
            "/api/reports/organization/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # ANONYMOUS
    # --------------------------------------------------

    def test_anonymous_is_denied_personal_report(self):
        response = self.client.get(
            "/api/reports/summary/",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_anonymous_is_denied_team_report(self):
        response = self.client.get(
            "/api/reports/team/",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_anonymous_is_denied_organization_report(self):
        response = self.client.get(
            "/api/reports/organization/",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )
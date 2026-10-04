from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.clients.models import Client
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.tracker.models import TimeEntry, TimeEntryStatus


User = get_user_model()


class ReportsAPITestCase(APITestCase):

    def setUp(self):
        self.employee = User.objects.create_user(
            username="employee",
            email="employee@example.com",
            password="TestPass123!",
        )

        self.other_employee = User.objects.create_user(
            username="otheremployee",
            email="other@example.com",
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
            name="Reports API Client",
            company="Reports API Company",
        )

        self.second_client = Client.objects.create(
            owner=self.manager,
            name="Second API Client",
            company="Second Company",
        )

        self.project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Reports API Project",
            description="Reports API project",
            status="in_progress",
            hourly_rate=500,
        )

        self.completed_project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Completed API Project",
            description="Completed API project",
            status="completed",
            hourly_rate=600,
        )

        self.other_project = Project.objects.create(
            owner=self.admin,
            client=self.second_client,
            name="Other API Project",
            description="Other API project",
            status="in_progress",
            hourly_rate=700,
        )

        self.project.members.add(
            self.employee,
            self.other_employee,
        )

        self.completed_project.members.add(
            self.employee,
        )

        self.other_project.members.add(
            self.other_employee,
        )

        self.task = Task.objects.create(
            owner=self.manager,
            project=self.project,
            assigned_to=self.employee,
            title="Reports API Task",
            description="Reports API task",
            priority="medium",
            status="completed",
            estimated_hours=5,
            due_date=date.today(),
        )

        self._create_entry(
            owner=self.employee,
            project=self.project,
            task=self.task,
            hours=2,
            billable=True,
        )

        self._create_entry(
            owner=self.employee,
            project=self.completed_project,
            hours=1,
            billable=False,
        )

        self._create_entry(
            owner=self.other_employee,
            project=self.project,
            hours=3,
            billable=True,
        )

        self._create_entry(
            owner=self.other_employee,
            project=self.other_project,
            hours=4,
            billable=True,
        )

    def _create_entry(
        self,
        *,
        owner,
        project,
        hours,
        billable,
        task=None,
        days_ago=0,
    ):
        start_time = timezone.now() - timedelta(
            days=days_ago,
            hours=hours,
        )

        return TimeEntry.objects.create(
            owner=owner,
            project=project,
            task=task,
            description="Reports API entry",
            start_time=start_time,
            end_time=start_time + timedelta(
                hours=hours,
            ),
            billable=billable,
            hourly_rate=project.hourly_rate,
            status=TimeEntryStatus.COMPLETED,
        )

    # --------------------------------------------------
    # PERSONAL REPORTS
    # --------------------------------------------------

    def test_employee_can_get_summary(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            "/api/reports/summary/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["total_entries"],
            2,
        )

    def test_employee_can_get_daily_report(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            "/api/reports/me/daily/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "entries",
            response.data,
        )

    def test_employee_can_get_weekly_report(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            "/api/reports/me/weekly/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "week_start",
            response.data,
        )

    def test_employee_can_get_monthly_report(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            "/api/reports/me/monthly/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "month",
            response.data,
        )

    # --------------------------------------------------
    # TIMESHEET
    # --------------------------------------------------

    def test_employee_can_get_timesheet(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            "/api/reports/timesheet/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

    def test_timesheet_project_filter(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            "/api/reports/timesheet/",
            {
                "project": self.project.id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_timesheet_client_filter(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            "/api/reports/timesheet/",
            {
                "client": self.client_record.id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

    def test_timesheet_billable_filter(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            "/api/reports/timesheet/",
            {
                "billable": "true",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    # --------------------------------------------------
    # EXPORTS
    # --------------------------------------------------

    def test_csv_export_returns_csv_file(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            "/api/reports/timesheet/export/csv/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response["Content-Type"],
            "text/csv",
        )

        self.assertIn(
            "timesheet_report.csv",
            response["Content-Disposition"],
        )

        self.assertIn(
            b"Project",
            response.content,
        )

    def test_excel_export_returns_excel_file(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            "/api/reports/timesheet/export/excel/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        self.assertIn(
            "timesheet_report.xlsx",
            response["Content-Disposition"],
        )

    # --------------------------------------------------
    # PROJECT / CLIENT
    # --------------------------------------------------

    def test_client_report_without_entries_returns_empty_report(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            f"/api/reports/clients/{self.second_client.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIsNone(
            response.data["total_entries"],
        )

        self.assertIsNone(
            response.data["total_hours"],
        )

        self.assertIsNone(
            response.data["billable_hours"],
        )

        self.assertIsNone(
            response.data["non_billable_hours"],
        )

        self.assertIsNone(
            response.data["total_earnings"],
        )

        self.assertEqual(
            response.data["entries"],
            [],
        )

    def test_employee_member_can_get_project_report(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            f"/api/reports/projects/{self.project.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["total_entries"],
            2,
        )

        self.assertEqual(
            response.data["total_hours"],
            "5.00",
        )

        self.assertEqual(
            response.data["billable_hours"],
            "5.00",
        )

        self.assertEqual(
            response.data["non_billable_hours"],
            "0.00",
        )

    def test_employee_cannot_get_unowned_project_report(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            f"/api/reports/projects/{self.other_project.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_employee_can_get_client_report_with_entries(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            f"/api/reports/clients/{self.client_record.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["total_entries"],
            2,
        )

    # --------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------

    def test_employee_can_get_dashboard_analytics(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            "/api/reports/dashboard/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["completed_entries"],
            2,
        )

    def test_employee_can_get_productivity_analytics(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            "/api/reports/dashboard/productivity/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            7,
        )

    # --------------------------------------------------
    # TEAM
    # --------------------------------------------------

    def test_manager_can_get_team_report(self):
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

        self.assertEqual(
            response.data["total_projects"],
            2,
        )

        self.assertEqual(
            response.data["total_entries"],
            3,
        )

    def test_employee_cannot_get_team_report(self):
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

    def test_admin_can_get_team_report(self):
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

        self.assertIn(
            "projects",
            response.data,
        )

    # --------------------------------------------------
    # ORGANIZATION
    # --------------------------------------------------

    def test_admin_can_get_organization_report(self):
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

        self.assertEqual(
            response.data["total_projects"],
            3,
        )

        self.assertEqual(
            response.data["total_entries"],
            4,
        )

    def test_manager_cannot_get_organization_report(self):
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

    def test_employee_cannot_get_organization_report(self):
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

    # --------------------------------------------------
    # END
    # --------------------------------------------------
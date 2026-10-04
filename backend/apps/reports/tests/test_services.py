from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone

from apps.clients.models import Client
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.tracker.models import TimeEntry, TimeEntryStatus

from apps.reports.services import (
    get_client_report,
    get_dashboard_analytics,
    get_daily_report,
    get_monthly_report,
    get_organization_report,
    get_productivity_analytics,
    get_project_report,
    get_report_summary,
    get_team_report,
    get_timesheet_report,
    get_weekly_report,
)


User = get_user_model()


class ReportsServiceTestCase(TestCase):

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
            name="Reports Client",
            company="Reports Company",
        )

        self.second_client = Client.objects.create(
            owner=self.manager,
            name="Second Client",
            company="Second Company",
        )

        self.project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Reports Project",
            description="Reports project",
            status="in_progress",
            hourly_rate=500,
        )

        self.completed_project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Completed Project",
            description="Completed project",
            status="completed",
            hourly_rate=600,
        )

        self.other_project = Project.objects.create(
            owner=self.admin,
            client=self.second_client,
            name="Other Project",
            description="Other organization project",
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
            title="Reports Task",
            description="Reports task",
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
        status=TimeEntryStatus.COMPLETED,
    ):
        start_time = timezone.now() - timedelta(
            days=days_ago,
            hours=hours,
        )

        return TimeEntry.objects.create(
            owner=owner,
            project=project,
            task=task,
            description="Reports test entry",
            start_time=start_time,
            end_time=start_time + timedelta(
                hours=hours,
            ),
            billable=billable,
            hourly_rate=project.hourly_rate,
            status=status,
        )

    # --------------------------------------------------
    # COMPLETED ENTRY SCOPE
    # --------------------------------------------------

    def test_report_summary_only_counts_user_entries(self):
        summary = get_report_summary(
            self.employee,
        )

        self.assertEqual(
            summary["total_entries"],
            2,
        )

        self.assertEqual(
            summary["billable_entries"],
            1,
        )

        self.assertEqual(
            summary["non_billable_entries"],
            1,
        )

        self.assertEqual(
            summary["total_duration_hours"],
            3.0,
        )

        self.assertEqual(
            summary["billable_hours"],
            2.0,
        )

    # --------------------------------------------------
    # TIMESHEET
    # --------------------------------------------------

    def test_timesheet_returns_only_user_entries(self):
        entries = get_timesheet_report(
            user=self.employee,
        )

        self.assertEqual(
            entries.count(),
            2,
        )

        self.assertTrue(
            all(
                entry.owner_id == self.employee.id
                for entry in entries
            )
        )

    def test_timesheet_project_filter(self):
        entries = get_timesheet_report(
            user=self.employee,
            project_id=self.project.id,
        )

        self.assertEqual(
            entries.count(),
            1,
        )

        self.assertEqual(
            entries.first().project_id,
            self.project.id,
        )

    def test_timesheet_client_filter(self):
        entries = get_timesheet_report(
            user=self.employee,
            client_id=self.client_record.id,
        )

        self.assertEqual(
            entries.count(),
            2,
        )

    def test_timesheet_billable_filter(self):
        entries = get_timesheet_report(
            user=self.employee,
            billable=True,
        )

        self.assertEqual(
            entries.count(),
            1,
        )

        self.assertTrue(
            entries.first().billable,
        )

    def test_timesheet_non_billable_filter(self):
        entries = get_timesheet_report(
            user=self.employee,
            billable=False,
        )

        self.assertEqual(
            entries.count(),
            1,
        )

        self.assertFalse(
            entries.first().billable,
        )

    def test_timesheet_invalid_ordering_falls_back_to_default(self):
        entries = get_timesheet_report(
            user=self.employee,
            ordering="invalid-ordering",
        )

        self.assertEqual(
            entries.count(),
            2,
        )

    # --------------------------------------------------
    # DAILY
    # --------------------------------------------------

    def test_daily_report_returns_expected_structure(self):
        report = get_daily_report(
            user=self.employee,
        )

        self.assertIn(
            "date",
            report,
        )

        self.assertIn(
            "total_entries",
            report,
        )

        self.assertIn(
            "total_hours",
            report,
        )

        self.assertIn(
            "billable_hours",
            report,
        )

        self.assertIn(
            "non_billable_hours",
            report,
        )

        self.assertIn(
            "total_earnings",
            report,
        )

        self.assertIn(
            "entries",
            report,
        )

    # --------------------------------------------------
    # WEEKLY
    # --------------------------------------------------

    def test_weekly_report_returns_expected_structure(self):
        report = get_weekly_report(
            user=self.employee,
        )

        self.assertIn(
            "week_start",
            report,
        )

        self.assertIn(
            "week_end",
            report,
        )

        self.assertIn(
            "total_entries",
            report,
        )

        self.assertIn(
            "entries",
            report,
        )

        self.assertGreaterEqual(
            report["total_entries"],
            0,
        )

    # --------------------------------------------------
    # MONTHLY
    # --------------------------------------------------

    def test_monthly_report_returns_current_month(self):
        report = get_monthly_report(
            user=self.employee,
        )

        self.assertEqual(
            report["year"],
            timezone.localdate().year,
        )

        self.assertEqual(
            report["month"],
            timezone.localdate().strftime("%B"),
        )

    # --------------------------------------------------
    # PROJECT REPORT
    # --------------------------------------------------

    def test_project_report_returns_project_entries(self):
        report = get_project_report(
            user=self.manager,
            project_id=self.project.id,
        )

        self.assertEqual(
            report["project"].id,
            self.project.id,
        )

        self.assertEqual(
            report["total_entries"],
            2,
        )

        self.assertEqual(
            report["total_hours"],
            Decimal("5.00"),
        )

    def test_project_report_calculates_billable_hours(self):
        report = get_project_report(
            user=self.manager,
            project_id=self.project.id,
        )

        self.assertEqual(
            report["billable_hours"],
            Decimal("5.00"),
        )

    # --------------------------------------------------
    # CLIENT REPORT
    # --------------------------------------------------

    def test_client_report_returns_matching_entries(self):
        report = get_client_report(
            user=self.employee,
            client_id=self.client_record.id,
        )

        self.assertIsNotNone(
            report,
        )

        self.assertEqual(
            report["client"].id,
            self.client_record.id,
        )

        self.assertEqual(
            report["total_entries"],
            2,
        )

    def test_client_report_returns_none_without_entries(self):
        report = get_client_report(
            user=self.employee,
            client_id=self.second_client.id,
        )

        self.assertIsNone(
            report,
        )

    # --------------------------------------------------
    # DASHBOARD ANALYTICS
    # --------------------------------------------------

    def test_dashboard_analytics_returns_expected_fields(self):
        analytics = get_dashboard_analytics(
            user=self.employee,
        )

        expected_fields = {
            "today_hours",
            "week_hours",
            "month_hours",
            "completed_entries",
            "billable_hours",
            "non_billable_hours",
            "estimated_earnings",
            "active_projects",
            "completed_projects",
            "top_project",
            "top_client",
        }

        self.assertTrue(
            expected_fields.issubset(
                analytics.keys()
            )
        )

    def test_dashboard_analytics_counts_completed_entries(self):
        analytics = get_dashboard_analytics(
            user=self.employee,
        )

        self.assertEqual(
            analytics["completed_entries"],
            2,
        )

    def test_dashboard_analytics_counts_billable_hours(self):
        analytics = get_dashboard_analytics(
            user=self.employee,
        )

        self.assertEqual(
            analytics["billable_hours"],
            Decimal("2.00"),
        )

    # --------------------------------------------------
    # PRODUCTIVITY
    # --------------------------------------------------

    def test_productivity_returns_seven_days(self):
        results = get_productivity_analytics(
            user=self.employee,
        )

        self.assertEqual(
            len(results),
            7,
        )

    def test_productivity_dates_are_consecutive(self):
        results = get_productivity_analytics(
            user=self.employee,
        )

        dates = [
            result["date"]
            for result in results
        ]

        for first, second in zip(
            dates,
            dates[1:],
        ):
            self.assertEqual(
                second - first,
                timedelta(days=1),
            )

    # --------------------------------------------------
    # TEAM REPORT
    # --------------------------------------------------

    def test_team_report_only_includes_manager_owned_projects(self):
        report = get_team_report(
            user=self.manager,
        )

        project_ids = {
            project["id"]
            for project in report["projects"]
        }

        self.assertIn(
            self.project.id,
            project_ids,
        )

        self.assertIn(
            self.completed_project.id,
            project_ids,
        )

        self.assertNotIn(
            self.other_project.id,
            project_ids,
        )

    def test_team_report_excludes_entries_from_other_projects(self):
        report = get_team_report(
            user=self.manager,
        )

        self.assertEqual(
            report["total_entries"],
            3,
        )

    def test_team_report_returns_team_members(self):
        report = get_team_report(
            user=self.manager,
        )

        usernames = {
            member["username"]
            for member in report["team_members"]
        }

        self.assertIn(
            self.employee.username,
            usernames,
        )

        self.assertIn(
            self.other_employee.username,
            usernames,
        )

    # --------------------------------------------------
    # ORGANIZATION REPORT
    # --------------------------------------------------

    def test_organization_report_includes_all_projects(self):
        report = get_organization_report(
            user=self.admin,
        )

        project_ids = {
            project["id"]
            for project in report["projects"]
        }

        self.assertIn(
            self.project.id,
            project_ids,
        )

        self.assertIn(
            self.completed_project.id,
            project_ids,
        )

        self.assertIn(
            self.other_project.id,
            project_ids,
        )

    def test_organization_report_counts_all_completed_entries(self):
        report = get_organization_report(
            user=self.admin,
        )

        self.assertEqual(
            report["total_entries"],
            4,
        )

    def test_organization_report_counts_all_hours(self):
        report = get_organization_report(
            user=self.admin,
        )

        self.assertEqual(
            report["total_hours"],
            Decimal("10.00"),
        )

    def test_organization_report_separates_billable_hours(self):
        report = get_organization_report(
            user=self.admin,
        )

        self.assertEqual(
            report["billable_hours"],
            Decimal("9.00"),
        )

        self.assertEqual(
            report["non_billable_hours"],
            Decimal("1.00"),
        )

    def test_organization_report_contains_active_users(self):
        report = get_organization_report(
            user=self.admin,
        )

        usernames = {
            member["username"]
            for member in report["team_members"]
        }

        self.assertIn(
            self.employee.username,
            usernames,
        )

        self.assertIn(
            self.other_employee.username,
            usernames,
        )

        self.assertIn(
            self.manager.username,
            usernames,
        )

        self.assertIn(
            self.admin.username,
            usernames,
        )
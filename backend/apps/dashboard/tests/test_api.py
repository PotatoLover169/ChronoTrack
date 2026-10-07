from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
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


class DashboardAPITestCase(TestCase):

    def setUp(self):
        self.client_api = APIClient()

        self.user = User.objects.create_user(
            username="dashboard_api_user",
            email="dashboard_api@example.com",
            password="TestPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="dashboard_api_other",
            email="other_dashboard_api@example.com",
            password="TestPassword123!",
        )

        self.client = Client.objects.create(
            owner=self.user,
            name="API Dashboard Client",
            company="Dashboard API Company",
        )

        self.other_client = Client.objects.create(
            owner=self.other_user,
            name="Other API Client",
        )

        self.project = Project.objects.create(
            owner=self.user,
            client=self.client,
            name="API Dashboard Project",
            status="in_progress",
            hourly_rate=Decimal("100.00"),
        )

        self.other_project = Project.objects.create(
            owner=self.other_user,
            client=self.other_client,
            name="Other User Project",
            status="in_progress",
            hourly_rate=Decimal("200.00"),
        )

    def authenticate(self):
        self.client_api.force_authenticate(
            user=self.user
        )

    def create_completed_entry(
        self,
        *,
        owner=None,
        project=None,
        description="API dashboard entry",
        billable=True,
        hours=2,
    ):
        owner = owner or self.user
        project = project or self.project

        start_time = timezone.now() - timedelta(
            hours=hours
        )

        return TimeEntry.objects.create(
            owner=owner,
            project=project,
            description=description,
            start_time=start_time,
            end_time=timezone.now(),
            billable=billable,
            status=TimeEntryStatus.COMPLETED,
        )

    def test_health_endpoint_is_public(self):
        response = self.client_api.get(
            "/api/dashboard/health/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["status"],
            "success",
        )

        self.assertEqual(
            response.data["message"],
            "ChronoTrack API is running",
        )

        self.assertEqual(
            response.data["version"],
            "1.0.0",
        )

    def test_dashboard_requires_authentication(self):
        response = self.client_api.get(
            "/api/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_dashboard_returns_authenticated_user_data(self):
        self.authenticate()

        self.create_completed_entry(
            description="User dashboard work",
        )

        response = self.client_api.get(
            "/api/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "summary",
            response.data,
        )

        self.assertIn(
            "recent_entries",
            response.data,
        )

        self.assertIn(
            "top_projects",
            response.data,
        )

        self.assertIn(
            "hours_per_day",
            response.data,
        )

        self.assertIn(
            "billable_breakdown",
            response.data,
        )

        self.assertIn(
            "project_status_breakdown",
            response.data,
        )

        self.assertIn(
            "charts",
            response.data,
        )

        self.assertEqual(
            response.data["summary"]["active_projects"],
            1,
        )

    def test_dashboard_does_not_expose_other_users_entries(self):
        self.authenticate()

        self.create_completed_entry(
            description="My private entry",
        )

        self.create_completed_entry(
            owner=self.other_user,
            project=self.other_project,
            description="Other user's private entry",
        )

        response = self.client_api.get(
            "/api/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        descriptions = [
            item["description"]
            for item in response.data["recent_entries"]
        ]

        self.assertIn(
            "My private entry",
            descriptions,
        )

        self.assertNotIn(
            "Other user's private entry",
            descriptions,
        )

    def test_recent_entries_endpoint(self):
        self.authenticate()

        self.create_completed_entry(
            description="Recent API entry",
        )

        response = self.client_api.get(
            "/api/dashboard/recent-entries/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["description"],
            "Recent API entry",
        )

    def test_recent_projects_endpoint(self):
        self.authenticate()

        response = self.client_api.get(
            "/api/dashboard/recent-projects/"
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
            "API Dashboard Project",
            names,
        )

        self.assertNotIn(
            "Other User Project",
            names,
        )

    def test_upcoming_tasks_endpoint(self):
        self.authenticate()

        task = Task.objects.create(
            owner=self.user,
            project=self.project,
            title="Upcoming API Task",
            due_date=timezone.localdate() + timedelta(
                days=2
            ),
            status="todo",
            completed=False,
        )

        response = self.client_api.get(
            "/api/dashboard/upcoming-tasks/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        titles = [
            item["title"]
            for item in response.data
        ]

        self.assertIn(
            task.title,
            titles,
        )

    def test_overdue_tasks_endpoint(self):
        self.authenticate()

        task = Task.objects.create(
            owner=self.user,
            project=self.project,
            title="Overdue API Task",
            due_date=timezone.localdate() - timedelta(
                days=2
            ),
            status="todo",
            completed=False,
        )

        response = self.client_api.get(
            "/api/dashboard/overdue-tasks/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        titles = [
            item["title"]
            for item in response.data
        ]

        self.assertIn(
            task.title,
            titles,
        )

    def test_active_timer_endpoint_returns_none_when_no_timer_exists(self):
        self.authenticate()

        response = self.client_api.get(
            "/api/dashboard/active-timer/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsNone(
            response.data
        )

    def test_active_timer_endpoint_returns_running_timer(self):
        self.authenticate()

        timer = TimeEntry.objects.create(
            owner=self.user,
            project=self.project,
            description="Running API timer",
            start_time=timezone.now() - timedelta(
                minutes=5
            ),
            status=TimeEntryStatus.RUNNING,
        )

        response = self.client_api.get(
            "/api/dashboard/active-timer/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["id"],
            timer.id,
        )

        self.assertEqual(
            response.data["description"],
            "Running API timer",
        )

        self.assertGreaterEqual(
            response.data["elapsed_seconds"],
            300,
        )

    def test_quick_stats_endpoint(self):
        self.authenticate()

        self.create_completed_entry(
            hours=2,
        )

        response = self.client_api.get(
            "/api/dashboard/quick-stats/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["today_hours"],
            2.0,
        )

        self.assertEqual(
            response.data["this_week_hours"],
            2.0,
        )

        self.assertEqual(
            response.data["this_month_hours"],
            2.0,
        )

        self.assertEqual(
            response.data["active_projects"],
            1,
        )

    def test_feed_endpoint(self):
        self.authenticate()

        self.create_completed_entry(
            description="Feed time entry",
        )

        Task.objects.create(
            owner=self.user,
            project=self.project,
            title="Feed task",
            status="todo",
        )

        response = self.client_api.get(
            "/api/dashboard/feed/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        types = [
            item["type"]
            for item in response.data
        ]

        self.assertIn(
            "time_entry",
            types,
        )

        self.assertIn(
            "project",
            types,
        )

        self.assertIn(
            "task",
            types,
        )

    def test_dashboard_endpoints_require_authentication(self):
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
                response = self.client_api.get(
                    endpoint
                )

                self.assertEqual(
                    response.status_code,
                    401,
                )
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.approvals.models import (
    EditRequestStatus,
    TimeEntryEditRequest,
)
from apps.clients.models import Client
from apps.dashboard.services import (
    build_productivity_summary,
    get_active_projects,
    get_active_timer,
    get_billable_breakdown,
    get_billable_hours,
    get_chart_data,
    get_completed_entries,
    get_completed_projects,
    get_current_timer,
    get_dashboard_data,
    get_dashboard_feed,
    get_estimated_earnings,
    get_hours_per_day,
    get_month_summary,
    get_overdue_tasks,
    get_pending_approvals,
    get_project_status_breakdown,
    get_quick_stats,
    get_recent_entries,
    get_recent_projects,
    get_running_timer,
    get_this_month_hours,
    get_this_week_hours,
    get_today_hours,
    get_today_summary,
    get_total_clients,
    get_top_projects,
    get_upcoming_tasks,
    get_week_summary,
)
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.tracker.models import (
    TimeEntry,
    TimeEntryStatus,
)


User = get_user_model()


class DashboardServicesTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="dashboard_user",
            email="dashboard@example.com",
            password="TestPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="other_dashboard_user",
            email="other@example.com",
            password="TestPassword123!",
        )

        self.client = Client.objects.create(
            owner=self.user,
            name="Dashboard Client",
            company="Dashboard Company",
            email="client@example.com",
        )

        self.other_client = Client.objects.create(
            owner=self.other_user,
            name="Other Client",
        )

        self.project = Project.objects.create(
            owner=self.user,
            client=self.client,
            name="Dashboard Project",
            status="in_progress",
            hourly_rate=Decimal("100.00"),
        )

        self.completed_project = Project.objects.create(
            owner=self.user,
            client=self.client,
            name="Completed Project",
            status="completed",
            hourly_rate=Decimal("100.00"),
        )

        self.planning_project = Project.objects.create(
            owner=self.user,
            client=self.client,
            name="Planning Project",
            status="planning",
            hourly_rate=Decimal("100.00"),
        )

        self.other_project = Project.objects.create(
            owner=self.other_user,
            client=self.other_client,
            name="Other User Project",
            status="in_progress",
            hourly_rate=Decimal("200.00"),
        )

    def create_time_entry(
        self,
        *,
        owner=None,
        project=None,
        task=None,
        start_time=None,
        duration_hours=1,
        billable=True,
        status=TimeEntryStatus.COMPLETED,
        description="Dashboard test entry",
    ):
        owner = owner or self.user
        project = project or self.project
        start_time = start_time or timezone.now()

        end_time = None

        if status == TimeEntryStatus.COMPLETED:
            end_time = start_time + timedelta(
                hours=duration_hours
            )

        return TimeEntry.objects.create(
            owner=owner,
            project=project,
            task=task,
            description=description,
            start_time=start_time,
            end_time=end_time,
            billable=billable,
            status=status,
        )

    def test_get_completed_entries_returns_only_completed_entries_for_user(self):
        completed = self.create_time_entry()

        self.create_time_entry(
            status=TimeEntryStatus.RUNNING,
        )

        self.create_time_entry(
            owner=self.other_user,
            project=self.other_project,
        )

        entries = get_completed_entries(self.user)

        self.assertEqual(entries.count(), 1)
        self.assertEqual(entries.first(), completed)

    def test_running_timer_detection(self):
        self.assertFalse(
            get_running_timer(self.user)
        )

        self.create_time_entry(
            status=TimeEntryStatus.RUNNING,
        )

        self.assertTrue(
            get_running_timer(self.user)
        )

    def test_current_timer_returns_timer_data(self):
        start_time = timezone.now() - timedelta(
            minutes=10
        )

        timer = self.create_time_entry(
            start_time=start_time,
            status=TimeEntryStatus.RUNNING,
            description="Current dashboard timer",
        )

        result = get_current_timer(self.user)

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], timer.id)
        self.assertEqual(
            result["project"],
            self.project,
        )
        self.assertEqual(
            result["description"],
            "Current dashboard timer",
        )
        self.assertGreaterEqual(
            result["elapsed_seconds"],
            600,
        )

    def test_current_timer_returns_none_when_not_running(self):
        self.assertIsNone(
            get_current_timer(self.user)
        )

    def test_build_productivity_summary(self):
        first = self.create_time_entry(
            duration_hours=2,
            billable=True,
        )

        second = self.create_time_entry(
            duration_hours=1,
            billable=False,
        )

        entries = TimeEntry.objects.filter(
            id__in=[first.id, second.id]
        )

        summary = build_productivity_summary(
            entries
        )

        self.assertEqual(
            summary["hours"],
            3.0,
        )

        self.assertEqual(
            summary["billable_hours"],
            2.0,
        )

        self.assertEqual(
            summary["earnings"],
            Decimal("200.00"),
        )

        self.assertEqual(
            summary["entries"],
            2,
        )

        self.assertEqual(
            summary["completed_tasks"],
            0,
        )

    def test_today_summary(self):
        self.create_time_entry(
            duration_hours=2,
            billable=True,
            start_time=timezone.now(),
        )

        summary = get_today_summary(
            self.user
        )

        self.assertEqual(
            summary["hours"],
            2.0,
        )

        self.assertEqual(
            summary["billable_hours"],
            2.0,
        )

        self.assertEqual(
            summary["earnings"],
            Decimal("200.00"),
        )

        self.assertEqual(
            summary["entries"],
            1,
        )

    def test_week_summary(self):
        self.create_time_entry(
            duration_hours=3,
            start_time=timezone.now(),
        )

        summary = get_week_summary(
            self.user
        )

        self.assertEqual(
            summary["hours"],
            3.0,
        )

    def test_month_summary(self):
        self.create_time_entry(
            duration_hours=4,
            start_time=timezone.now(),
        )

        summary = get_month_summary(
            self.user
        )

        self.assertEqual(
            summary["hours"],
            4.0,
        )

    def test_today_week_and_month_hours(self):
        self.create_time_entry(
            duration_hours=2,
        )

        self.assertEqual(
            get_today_hours(self.user),
            2.0,
        )

        self.assertEqual(
            get_this_week_hours(self.user),
            2.0,
        )

        self.assertEqual(
            get_this_month_hours(self.user),
            2.0,
        )

    def test_billable_hours(self):
        self.create_time_entry(
            duration_hours=2,
            billable=True,
        )

        self.create_time_entry(
            duration_hours=3,
            billable=False,
        )

        self.assertEqual(
            get_billable_hours(self.user),
            2.0,
        )

    def test_estimated_earnings(self):
        self.create_time_entry(
            duration_hours=2,
            billable=True,
        )

        self.create_time_entry(
            duration_hours=1,
            billable=False,
        )

        self.assertEqual(
            get_estimated_earnings(self.user),
            Decimal("200.00"),
        )

    def test_project_counts(self):
        self.assertEqual(
            get_active_projects(self.user),
            1,
        )

        self.assertEqual(
            get_completed_projects(self.user),
            1,
        )

    def test_total_clients(self):
        self.assertEqual(
            get_total_clients(self.user),
            1,
        )

    def test_pending_approvals(self):
        entry = self.create_time_entry()

        TimeEntryEditRequest.objects.create(
            time_entry=entry,
            requested_by=self.user,
            reason="Need to correct time",
            status=EditRequestStatus.PENDING,
        )

        self.assertEqual(
            get_pending_approvals(),
            1,
        )

    def test_recent_entries_are_ordered_and_limited(self):
        now = timezone.now()

        oldest = self.create_time_entry(
            start_time=now - timedelta(hours=3),
        )

        newest = self.create_time_entry(
            start_time=now - timedelta(hours=1),
        )

        entries = get_recent_entries(
            self.user,
            limit=1,
        )

        self.assertEqual(
            entries.count(),
            1,
        )

        self.assertEqual(
            entries.first(),
            newest,
        )

        self.assertNotEqual(
            entries.first(),
            oldest,
        )

    def test_recent_projects_are_ordered_and_limited(self):
        self.project.save()

        projects = get_recent_projects(
            self.user,
            limit=2,
        )

        self.assertEqual(
            projects.count(),
            2,
        )

        self.assertIn(
            self.project,
            projects,
        )

    def test_upcoming_tasks_returns_future_incomplete_tasks(self):
        tomorrow = timezone.localdate() + timedelta(
            days=1
        )

        task = Task.objects.create(
            owner=self.user,
            project=self.project,
            title="Upcoming Dashboard Task",
            due_date=tomorrow,
            status="todo",
            completed=False,
        )

        tasks = get_upcoming_tasks(
            self.user
        )

        self.assertIn(
            task,
            tasks,
        )

    def test_upcoming_tasks_excludes_completed_tasks(self):
        tomorrow = timezone.localdate() + timedelta(
            days=1
        )

        task = Task.objects.create(
            owner=self.user,
            project=self.project,
            title="Completed Future Task",
            due_date=tomorrow,
            status="completed",
            completed=True,
        )

        tasks = get_upcoming_tasks(
            self.user
        )

        self.assertNotIn(
            task,
            tasks,
        )

    def test_overdue_tasks_returns_incomplete_past_tasks(self):
        yesterday = timezone.localdate() - timedelta(
            days=1
        )

        task = Task.objects.create(
            owner=self.user,
            project=self.project,
            title="Overdue Dashboard Task",
            due_date=yesterday,
            status="todo",
            completed=False,
        )

        tasks = get_overdue_tasks(
            self.user
        )

        self.assertIn(
            task,
            tasks,
        )

    def test_overdue_tasks_excludes_completed_tasks(self):
        yesterday = timezone.localdate() - timedelta(
            days=1
        )

        task = Task.objects.create(
            owner=self.user,
            project=self.project,
            title="Completed Overdue Task",
            due_date=yesterday,
            status="completed",
            completed=True,
        )

        tasks = get_overdue_tasks(
            self.user
        )

        self.assertNotIn(
            task,
            tasks,
        )

    def test_get_active_timer(self):
        timer = self.create_time_entry(
            status=TimeEntryStatus.RUNNING,
        )

        result = get_active_timer(
            self.user
        )

        self.assertEqual(
            result,
            timer,
        )

    def test_get_top_projects(self):
        self.create_time_entry(
            project=self.project,
            duration_hours=2,
        )

        self.create_time_entry(
            project=self.completed_project,
            duration_hours=5,
        )

        projects = get_top_projects(
            self.user
        )

        self.assertEqual(
            projects[0]["project"],
            self.completed_project,
        )

        self.assertEqual(
            projects[0]["hours"],
            5.0,
        )

    def test_get_hours_per_day_returns_requested_number_of_days(self):
        results = get_hours_per_day(
            self.user,
            days=7,
        )

        self.assertEqual(
            len(results),
            7,
        )

        for item in results:
            self.assertIn(
                "date",
                item,
            )

            self.assertIn(
                "hours",
                item,
            )

    def test_get_hours_per_day_includes_today_hours(self):
        self.create_time_entry(
            duration_hours=2,
        )

        results = get_hours_per_day(
            self.user,
            days=7,
        )

        today = timezone.localdate().isoformat()

        today_result = next(
            item
            for item in results
            if item["date"] == today
        )

        self.assertEqual(
            today_result["hours"],
            2.0,
        )

    def test_billable_breakdown(self):
        self.create_time_entry(
            duration_hours=2,
            billable=True,
        )

        self.create_time_entry(
            duration_hours=3,
            billable=False,
        )

        result = get_billable_breakdown(
            self.user
        )

        self.assertEqual(
            result["billable_hours"],
            2.0,
        )

        self.assertEqual(
            result["non_billable_hours"],
            3.0,
        )

    def test_project_status_breakdown(self):
        result = get_project_status_breakdown(
            self.user
        )

        self.assertEqual(
            result["planning"],
            1,
        )

        self.assertEqual(
            result["in_progress"],
            1,
        )

        self.assertEqual(
            result["completed"],
            1,
        )

        self.assertEqual(
            result["on_hold"],
            0,
        )

        self.assertEqual(
            result["cancelled"],
            0,
        )

    def test_chart_data(self):
        result = get_chart_data(
            self.user
        )

        self.assertIn(
            "hours_per_day",
            result,
        )

        self.assertIn(
            "billable",
            result,
        )

        self.assertIn(
            "project_status",
            result,
        )

        self.assertEqual(
            len(result["hours_per_day"]),
            7,
        )

        self.assertEqual(
            len(result["billable"]),
            2,
        )

        self.assertEqual(
            len(result["project_status"]),
            5,
        )

    def test_quick_stats(self):
        self.create_time_entry(
            duration_hours=2,
        )

        result = get_quick_stats(
            self.user
        )

        self.assertEqual(
            result["today_hours"],
            2.0,
        )

        self.assertEqual(
            result["this_week_hours"],
            2.0,
        )

        self.assertEqual(
            result["this_month_hours"],
            2.0,
        )

        self.assertEqual(
            result["active_projects"],
            1,
        )

        self.assertEqual(
            result["completed_projects"],
            1,
        )

        self.assertEqual(
            result["total_clients"],
            1,
        )

        self.assertEqual(
            result["billable_hours"],
            2.0,
        )

        self.assertEqual(
            result["estimated_earnings"],
            Decimal("200.00"),
        )

    def test_dashboard_feed_contains_recent_activity(self):
        entry = self.create_time_entry(
            description="Tracked dashboard work",
        )

        task = Task.objects.create(
            owner=self.user,
            project=self.project,
            title="Dashboard Task",
            status="todo",
        )

        activities = get_dashboard_feed(
            self.user
        )

        types = [
            item["type"]
            for item in activities
        ]

        descriptions = [
            item["description"]
            for item in activities
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

        self.assertIn(
            "Tracked dashboard work",
            descriptions,
        )

        self.assertIn(
            self.project.name,
            descriptions,
        )

        self.assertIn(
            task.title,
            descriptions,
        )

    def test_dashboard_data_contains_all_major_sections(self):
        result = get_dashboard_data(
            self.user
        )

        expected_keys = {
            "summary",
            "recent_entries",
            "top_projects",
            "hours_per_day",
            "billable_breakdown",
            "project_status_breakdown",
            "charts",
        }

        self.assertEqual(
            set(result.keys()),
            expected_keys,
        )

        self.assertIn(
            "running_timer",
            result["summary"],
        )

        self.assertIn(
            "current_timer",
            result["summary"],
        )

        self.assertIn(
            "today",
            result["summary"],
        )

        self.assertIn(
            "week",
            result["summary"],
        )

        self.assertIn(
            "month",
            result["summary"],
        )
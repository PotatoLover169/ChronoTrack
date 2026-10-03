from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.clients.models import Client
from apps.projects.models import Project
from apps.tasks.models import Task

from apps.tracker.exceptions import (
    NoRunningTimerError,
    TimerAlreadyRunningError,
)
from apps.tracker.models import (
    TimeEntry,
    TimeEntryStatus,
)
from apps.tracker.services import (
    get_current_timer,
    start_timer,
    stop_timer,
    validate_timer_access,
)


User = get_user_model()


class TrackerServiceTestCase(TestCase):

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
            name="Manager"
        )

        self.manager.groups.add(manager_group)

        self.client_record = Client.objects.create(
            owner=self.manager,
            name="Tracker Test Client",
            company="Tracker Test Company",
        )

        self.project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Tracker Project",
            description="Tracker service project",
            status="in_progress",
            hourly_rate=500,
        )

        self.project.members.add(
            self.employee,
            self.other_employee,
        )

        self.task = Task.objects.create(
            owner=self.manager,
            project=self.project,
            assigned_to=self.employee,
            title="Tracker Task",
            description="Tracker service task",
            priority="medium",
            status="todo",
            estimated_hours=5,
            due_date=date.today(),
        )

        self.other_task = Task.objects.create(
            owner=self.manager,
            project=self.project,
            assigned_to=self.other_employee,
            title="Other Employee Task",
            description="Other task",
            priority="low",
            status="todo",
            estimated_hours=3,
            due_date=date.today(),
        )

    # --------------------------------------------------
    # START TIMER
    # --------------------------------------------------

    def test_employee_can_start_timer_on_assigned_project(self):
        entry = start_timer(
            user=self.employee,
            project=self.project,
            description="Working on tracker",
        )

        self.assertEqual(
            entry.owner,
            self.employee,
        )

        self.assertEqual(
            entry.project,
            self.project,
        )

        self.assertEqual(
            entry.status,
            TimeEntryStatus.RUNNING,
        )

        self.assertIsNotNone(
            entry.start_time,
        )

    def test_employee_can_start_timer_with_assigned_task(self):
        entry = start_timer(
            user=self.employee,
            project=self.project,
            task=self.task,
            description="Working on task",
        )

        self.assertEqual(
            entry.task,
            self.task,
        )

        self.assertEqual(
            entry.status,
            TimeEntryStatus.RUNNING,
        )

    def test_manager_can_start_timer_on_any_project(self):
        entry = start_timer(
            user=self.manager,
            project=self.project,
        )

        self.assertEqual(
            entry.owner,
            self.manager,
        )

        self.assertEqual(
            entry.status,
            TimeEntryStatus.RUNNING,
        )

    def test_admin_can_start_timer_on_any_project(self):
        entry = start_timer(
            user=self.admin,
            project=self.project,
        )

        self.assertEqual(
            entry.owner,
            self.admin,
        )

        self.assertEqual(
            entry.status,
            TimeEntryStatus.RUNNING,
        )

    def test_start_timer_prevents_second_running_timer(self):
        start_timer(
            user=self.employee,
            project=self.project,
        )

        with self.assertRaises(
            TimerAlreadyRunningError
        ):
            start_timer(
                user=self.employee,
                project=self.project,
            )

    # --------------------------------------------------
    # TIMER ACCESS
    # --------------------------------------------------

    def test_employee_cannot_start_timer_on_unassigned_project(self):
        other_project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Other Project",
            description="Not assigned project",
            status="in_progress",
            hourly_rate=300,
        )

        with self.assertRaises(
            ValidationError
        ):
            start_timer(
                user=self.employee,
                project=other_project,
            )

    def test_employee_cannot_track_time_on_unassigned_task(self):
        with self.assertRaises(
            ValidationError
        ):
            start_timer(
                user=self.employee,
                project=self.project,
                task=self.other_task,
            )

    def test_manager_can_track_time_on_other_employee_task(self):
        entry = start_timer(
            user=self.manager,
            project=self.project,
            task=self.other_task,
        )

        self.assertEqual(
            entry.task,
            self.other_task,
        )

    def test_validate_timer_access_rejects_task_from_other_project(self):
        other_project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Second Project",
            description="Second project",
            status="in_progress",
            hourly_rate=400,
        )

        with self.assertRaises(
            ValidationError
        ):
            validate_timer_access(
                user=self.manager,
                project=other_project,
                task=self.task,
            )

    # --------------------------------------------------
    # CURRENT TIMER
    # --------------------------------------------------

    def test_get_current_timer_returns_running_timer(self):
        entry = start_timer(
            user=self.employee,
            project=self.project,
        )

        current = get_current_timer(
            user=self.employee,
        )

        self.assertIsNotNone(current)

        self.assertEqual(
            current.id,
            entry.id,
        )

    def test_get_current_timer_returns_none_without_running_timer(self):
        current = get_current_timer(
            user=self.employee,
        )

        self.assertIsNone(current)

    # --------------------------------------------------
    # STOP TIMER
    # --------------------------------------------------

    def test_stop_timer_completes_running_timer(self):
        entry = start_timer(
            user=self.employee,
            project=self.project,
        )

        stopped = stop_timer(
            user=self.employee,
        )

        stopped.refresh_from_db()

        self.assertEqual(
            stopped.id,
            entry.id,
        )

        self.assertEqual(
            stopped.status,
            TimeEntryStatus.COMPLETED,
        )

        self.assertIsNotNone(
            stopped.end_time,
        )

        self.assertIsNotNone(
            stopped.duration,
        )

        self.assertGreater(
            stopped.duration.total_seconds(),
            -1,
        )

    def test_stop_timer_without_running_timer_raises_error(self):
        with self.assertRaises(
            NoRunningTimerError
        ):
            stop_timer(
                user=self.employee,
            )

    # --------------------------------------------------
    # TIME ENTRY MODEL
    # --------------------------------------------------

    def test_time_entry_snapshots_project_hourly_rate(self):
        entry = start_timer(
            user=self.employee,
            project=self.project,
        )

        self.assertEqual(
            entry.hourly_rate,
            Decimal("500.00"),
        )

    def test_completed_time_entry_calculates_earnings(self):
        start_time = timezone.now()

        entry = TimeEntry.objects.create(
            owner=self.employee,
            project=self.project,
            description="Completed work",
            start_time=start_time,
            end_time=start_time
            + timezone.timedelta(hours=2),
            billable=True,
            status=TimeEntryStatus.COMPLETED,
        )

        entry.refresh_from_db()

        self.assertEqual(
            entry.duration.total_seconds(),
            7200,
        )

        self.assertEqual(
            entry.earnings,
            Decimal("1000.00"),
        )

    def test_non_billable_entry_has_zero_earnings(self):
        start_time = timezone.now()

        entry = TimeEntry.objects.create(
            owner=self.employee,
            project=self.project,
            description="Non-billable work",
            start_time=start_time,
            end_time=start_time
            + timezone.timedelta(hours=2),
            billable=False,
            status=TimeEntryStatus.COMPLETED,
        )

        self.assertEqual(
            entry.earnings,
            Decimal("0.00"),
        )
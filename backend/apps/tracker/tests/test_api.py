from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.clients.models import Client
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.tracker.models import (
    TimeEntry,
    TimeEntryStatus,
)


User = get_user_model()


class TrackerAPITestCase(APITestCase):

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
            name="Tracker API Client",
            company="Tracker API Company",
        )

        self.project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Tracker API Project",
            description="Tracker API project",
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
            title="Tracker API Task",
            description="Tracker API task",
            priority="medium",
            status="todo",
            estimated_hours=4,
            due_date=date.today(),
        )

        self.other_task = Task.objects.create(
            owner=self.manager,
            project=self.project,
            assigned_to=self.other_employee,
            title="Other Task",
            description="Other employee task",
            priority="low",
            status="todo",
            estimated_hours=2,
            due_date=date.today(),
        )

        self.list_url = "/api/tracker/"
        self.start_url = "/api/tracker/start/"
        self.stop_url = "/api/tracker/stop/"
        self.current_url = "/api/tracker/current/"

    # --------------------------------------------------
    # START TIMER
    # --------------------------------------------------

    def test_employee_can_start_timer(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.post(
            self.start_url,
            {
                "project": self.project.id,
                "description": "API timer test",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertIn(
            "time_entry_id",
            response.data,
        )

        entry = TimeEntry.objects.get(
            id=response.data["time_entry_id"]
        )

        self.assertEqual(
            entry.owner,
            self.employee,
        )

        self.assertEqual(
            entry.status,
            TimeEntryStatus.RUNNING,
        )

    def test_employee_can_start_timer_with_task(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.post(
            self.start_url,
            {
                "project": self.project.id,
                "task": self.task.id,
                "description": "Task timer test",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        entry = TimeEntry.objects.get(
            id=response.data["time_entry_id"]
        )

        self.assertEqual(
            entry.task,
            self.task,
        )

    def test_start_timer_rejects_task_from_wrong_project(self):
        self.client.force_authenticate(
            user=self.employee
        )

        other_project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Wrong Project",
            status="in_progress",
        )

        response = self.client.post(
            self.start_url,
            {
                "project": other_project.id,
                "task": self.task.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_employee_cannot_start_timer_on_unassigned_project(self):
        self.client.force_authenticate(
            user=self.employee
        )

        other_project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Private Project",
            status="in_progress",
        )

        response = self.client.post(
            self.start_url,
            {
                "project": other_project.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_employee_cannot_start_timer_on_unassigned_task(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.post(
            self.start_url,
            {
                "project": self.project.id,
                "task": self.other_task.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_starting_second_timer_returns_conflict(self):
        self.client.force_authenticate(
            user=self.employee
        )

        first_response = self.client.post(
            self.start_url,
            {
                "project": self.project.id,
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        second_response = self.client.post(
            self.start_url,
            {
                "project": self.project.id,
            },
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_409_CONFLICT,
        )

    # --------------------------------------------------
    # CURRENT TIMER
    # --------------------------------------------------

    def test_current_timer_returns_running_timer(self):
        self.client.force_authenticate(
            user=self.employee
        )

        start_response = self.client.post(
            self.start_url,
            {
                "project": self.project.id,
                "task": self.task.id,
                "description": "Current timer test",
            },
            format="json",
        )

        self.assertEqual(
            start_response.status_code,
            status.HTTP_201_CREATED,
        )

        response = self.client.get(
            self.current_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["status"],
            TimeEntryStatus.RUNNING,
        )

        self.assertEqual(
            response.data["project"]["id"],
            self.project.id,
        )

        self.assertEqual(
            response.data["task"]["id"],
            self.task.id,
        )

        self.assertIn(
            "elapsed_seconds",
            response.data,
        )

        self.assertIn(
            "elapsed_time",
            response.data,
        )

    def test_current_timer_returns_404_without_running_timer(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            self.current_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # --------------------------------------------------
    # STOP TIMER
    # --------------------------------------------------

    def test_stop_timer_completes_running_timer(self):
        self.client.force_authenticate(
            user=self.employee
        )

        start_response = self.client.post(
            self.start_url,
            {
                "project": self.project.id,
                "description": "Stop timer test",
            },
            format="json",
        )

        self.assertEqual(
            start_response.status_code,
            status.HTTP_201_CREATED,
        )

        entry_id = start_response.data[
            "time_entry_id"
        ]

        response = self.client.post(
            self.stop_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["time_entry_id"],
            entry_id,
        )

        entry = TimeEntry.objects.get(
            id=entry_id
        )

        self.assertEqual(
            entry.status,
            TimeEntryStatus.COMPLETED,
        )

        self.assertIsNotNone(
            entry.end_time,
        )

        self.assertIsNotNone(
            entry.duration,
        )

    def test_stop_timer_without_running_timer_returns_conflict(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.post(
            self.stop_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

    # --------------------------------------------------
    # TIME ENTRY LIST
    # --------------------------------------------------

    def test_employee_can_list_own_time_entries(self):
        self.client.force_authenticate(
            user=self.employee
        )

        TimeEntry.objects.create(
            owner=self.employee,
            project=self.project,
            task=self.task,
            description="Employee entry",
            start_time=timezone.now()
            - timedelta(hours=2),
            end_time=timezone.now()
            - timedelta(hours=1),
            billable=True,
            status=TimeEntryStatus.COMPLETED,
        )

        response = self.client.get(
            self.list_url
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
            response.data[0]["owner"]["id"],
            self.employee.id,
        )

    def test_employee_cannot_see_other_users_entries(self):
        TimeEntry.objects.create(
            owner=self.other_employee,
            project=self.project,
            description="Other employee entry",
            start_time=timezone.now()
            - timedelta(hours=2),
            end_time=timezone.now()
            - timedelta(hours=1),
            billable=True,
            status=TimeEntryStatus.COMPLETED,
        )

        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            0,
        )

    def test_manager_can_see_all_time_entries(self):
        TimeEntry.objects.create(
            owner=self.employee,
            project=self.project,
            description="Employee entry",
            start_time=timezone.now()
            - timedelta(hours=2),
            end_time=timezone.now()
            - timedelta(hours=1),
            status=TimeEntryStatus.COMPLETED,
        )

        TimeEntry.objects.create(
            owner=self.other_employee,
            project=self.project,
            description="Other entry",
            start_time=timezone.now()
            - timedelta(hours=3),
            end_time=timezone.now()
            - timedelta(hours=2),
            status=TimeEntryStatus.COMPLETED,
        )

        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

    def test_admin_can_see_all_time_entries(self):
        TimeEntry.objects.create(
            owner=self.employee,
            project=self.project,
            description="Employee entry",
            start_time=timezone.now()
            - timedelta(hours=2),
            end_time=timezone.now()
            - timedelta(hours=1),
            status=TimeEntryStatus.COMPLETED,
        )

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            self.list_url
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
    # FILTERS
    # --------------------------------------------------

    def test_project_filter(self):
        TimeEntry.objects.create(
            owner=self.employee,
            project=self.project,
            description="Project filter entry",
            start_time=timezone.now()
            - timedelta(hours=2),
            end_time=timezone.now()
            - timedelta(hours=1),
            status=TimeEntryStatus.COMPLETED,
        )

        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            self.list_url,
            {
                "project": self.project.id
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

    def test_task_filter(self):
        TimeEntry.objects.create(
            owner=self.employee,
            project=self.project,
            task=self.task,
            description="Task filter entry",
            start_time=timezone.now()
            - timedelta(hours=2),
            end_time=timezone.now()
            - timedelta(hours=1),
            status=TimeEntryStatus.COMPLETED,
        )

        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            self.list_url,
            {
                "task": self.task.id
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

    def test_status_filter(self):
        TimeEntry.objects.create(
            owner=self.employee,
            project=self.project,
            description="Completed entry",
            start_time=timezone.now()
            - timedelta(hours=2),
            end_time=timezone.now()
            - timedelta(hours=1),
            status=TimeEntryStatus.COMPLETED,
        )

        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            self.list_url,
            {
                "status": "completed"
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

    def test_billable_true_filter(self):
        TimeEntry.objects.create(
            owner=self.employee,
            project=self.project,
            description="Billable entry",
            start_time=timezone.now()
            - timedelta(hours=2),
            end_time=timezone.now()
            - timedelta(hours=1),
            billable=True,
            status=TimeEntryStatus.COMPLETED,
        )

        TimeEntry.objects.create(
            owner=self.employee,
            project=self.project,
            description="Non billable entry",
            start_time=timezone.now()
            - timedelta(hours=4),
            end_time=timezone.now()
            - timedelta(hours=3),
            billable=False,
            status=TimeEntryStatus.COMPLETED,
        )

        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            self.list_url,
            {
                "billable": "true"
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

        self.assertTrue(
            response.data[0]["billable"]
        )

    def test_billable_false_filter(self):
        TimeEntry.objects.create(
            owner=self.employee,
            project=self.project,
            description="Non billable entry",
            start_time=timezone.now()
            - timedelta(hours=2),
            end_time=timezone.now()
            - timedelta(hours=1),
            billable=False,
            status=TimeEntryStatus.COMPLETED,
        )

        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            self.list_url,
            {
                "billable": "false"
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

        self.assertFalse(
            response.data[0]["billable"]
        )

    def test_invalid_billable_filter_returns_400(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            self.list_url,
            {
                "billable": "invalid"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_start_date_returns_400(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            self.list_url,
            {
                "start_date": "2026-99-99"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_end_date_returns_400(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            self.list_url,
            {
                "end_date": "not-a-date"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_date_range_returns_400(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            self.list_url,
            {
                "start_date": "2026-10-10",
                "end_date": "2026-10-01",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------

    def test_unauthenticated_list_is_denied(self):
        response = self.client.get(
            self.list_url
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_unauthenticated_start_is_denied(self):
        response = self.client.post(
            self.start_url,
            {
                "project": self.project.id,
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )
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


class TrackerPermissionTestCase(APITestCase):

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
            self.other_employee,
        )

        self.task = Task.objects.create(
            owner=self.manager,
            project=self.project,
            assigned_to=self.employee,
            title="Permission Task",
            description="Permission task",
            priority="medium",
            status="todo",
            estimated_hours=3,
            due_date=date.today(),
        )

        self.entry = TimeEntry.objects.create(
            owner=self.employee,
            project=self.project,
            task=self.task,
            description="Permission entry",
            start_time=timezone.now()
            - timedelta(hours=2),
            end_time=timezone.now()
            - timedelta(hours=1),
            billable=True,
            status=TimeEntryStatus.COMPLETED,
        )

        self.list_url = "/api/tracker/"
        self.detail_url = (
            f"/api/tracker/{self.entry.id}/"
        )
        self.start_url = "/api/tracker/start/"
        self.stop_url = "/api/tracker/stop/"
        self.current_url = "/api/tracker/current/"

    # --------------------------------------------------
    # TIME ENTRY READ ACCESS
    # --------------------------------------------------

    def test_employee_can_read_own_entry(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_other_employee_cannot_read_entry(self):
        self.client.force_authenticate(
            user=self.other_employee
        )

        response = self.client.get(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_manager_can_read_entry(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.get(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_admin_can_read_entry(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # TIMER ACCESS
    # --------------------------------------------------

    def test_employee_can_start_timer_on_member_project(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.post(
            self.start_url,
            {
                "project": self.project.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_other_employee_can_start_timer_on_member_project(self):
        self.client.force_authenticate(
            user=self.other_employee
        )

        response = self.client.post(
            self.start_url,
            {
                "project": self.project.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_employee_cannot_start_timer_on_unassigned_project(self):
        private_project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Private Project",
            description="Private project",
            status="in_progress",
        )

        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.post(
            self.start_url,
            {
                "project": private_project.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_employee_cannot_track_other_employee_task(self):
        other_task = Task.objects.create(
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

        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.post(
            self.start_url,
            {
                "project": self.project.id,
                "task": other_task.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_manager_can_track_any_project_task(self):
        other_task = Task.objects.create(
            owner=self.manager,
            project=self.project,
            assigned_to=self.other_employee,
            title="Manager Task",
            description="Manager task",
            priority="medium",
            status="todo",
            estimated_hours=2,
            due_date=date.today(),
        )

        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.post(
            self.start_url,
            {
                "project": self.project.id,
                "task": other_task.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_admin_can_track_any_project_task(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            self.start_url,
            {
                "project": self.project.id,
                "task": self.task.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    # --------------------------------------------------
    # TIMER OWNERSHIP
    # --------------------------------------------------

    def test_employee_only_controls_own_timer(self):
        self.client.force_authenticate(
            user=self.employee
        )

        start_response = self.client.post(
            self.start_url,
            {
                "project": self.project.id,
            },
            format="json",
        )

        self.assertEqual(
            start_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(
            user=self.other_employee
        )

        stop_response = self.client.post(
            self.stop_url
        )

        self.assertEqual(
            stop_response.status_code,
            status.HTTP_409_CONFLICT,
        )

    # --------------------------------------------------
    # ANONYMOUS
    # --------------------------------------------------

    def test_anonymous_cannot_list_entries(self):
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

    def test_anonymous_cannot_start_timer(self):
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

    def test_anonymous_cannot_stop_timer(self):
        response = self.client.post(
            self.stop_url
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_anonymous_cannot_get_current_timer(self):
        response = self.client.get(
            self.current_url
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )
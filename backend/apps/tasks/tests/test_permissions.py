from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.clients.models import Client
from apps.projects.models import Project
from apps.tasks.models import Task


User = get_user_model()


class TaskPermissionTestCase(APITestCase):

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
            name="Permission Test Client",
            company="Permission Test Company",
        )

        self.project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Permission Project",
            status="in_progress",
        )

        self.project.members.add(
            self.employee
        )

        self.task = Task.objects.create(
            owner=self.manager,
            project=self.project,
            assigned_to=self.employee,
            title="Permission Task",
            description="Permission testing",
            priority="medium",
            status="todo",
            estimated_hours=2,
            due_date=date.today(),
        )

        self.list_url = "/api/tasks/"
        self.detail_url = (
            f"/api/tasks/{self.task.id}/"
        )

    # --------------------------------------------------
    # READ ACCESS
    # --------------------------------------------------

    def test_employee_can_read_assigned_task(self):
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

    def test_manager_can_read_task(self):
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

    def test_admin_can_read_task(self):
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
    # EMPLOYEE MUTATION RESTRICTIONS
    # --------------------------------------------------

    def test_employee_cannot_create_task(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.post(
            self.list_url,
            {
                "project_id": self.project.id,
                "title": "Unauthorized Task",
                "description": "Should fail",
                "priority": "medium",
                "status": "todo",
                "estimated_hours": 1,
                "due_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_employee_cannot_delete_task(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.delete(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_employee_can_patch_assigned_task(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.patch(
            self.detail_url,
            {
                "status": "in_progress"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # MANAGER / ADMIN MUTATION ACCESS
    # --------------------------------------------------

    def test_manager_can_create_task(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.post(
            self.list_url,
            {
                "project_id": self.project.id,
                "assigned_to_id": self.employee.id,
                "title": "Manager Task",
                "description": "Manager created",
                "priority": "medium",
                "status": "todo",
                "estimated_hours": 2,
                "due_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_manager_can_patch_task(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.patch(
            self.detail_url,
            {
                "title": "Manager Updated"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_manager_can_delete_task(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.delete(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

    def test_admin_can_create_task(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            self.list_url,
            {
                "project_id": self.project.id,
                "assigned_to_id": self.employee.id,
                "title": "Admin Task",
                "description": "Admin created",
                "priority": "low",
                "status": "todo",
                "estimated_hours": 1,
                "due_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_admin_can_patch_task(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.patch(
            self.detail_url,
            {
                "title": "Admin Updated"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_admin_can_delete_task(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.delete(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

    # --------------------------------------------------
    # ANONYMOUS
    # --------------------------------------------------

    def test_anonymous_cannot_read_tasks(self):
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

    def test_anonymous_cannot_create_tasks(self):
        response = self.client.post(
            self.list_url,
            {
                "project_id": self.project.id,
                "title": "Anonymous Task",
                "description": "Should fail",
                "priority": "medium",
                "status": "todo",
                "estimated_hours": 1,
                "due_date": str(date.today()),
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
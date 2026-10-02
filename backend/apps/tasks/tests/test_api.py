from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.clients.models import Client
from apps.projects.models import Project
from apps.tasks.models import Task


User = get_user_model()


class TaskAPITestCase(APITestCase):

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
            name="Test Client",
            company="Test Company",
        )

        self.project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Test Project",
            description="Task API test project",
            status="in_progress",
        )

        self.employee_project = Project.objects.create(
            owner=self.employee,
            client=self.client_record,
            name="Employee Project",
            description="Employee-owned project",
            status="in_progress",
        )

        self.project.members.add(
            self.employee,
            self.other_employee,
        )

        self.employee_project.members.add(
            self.employee,
        )

        self.assigned_task = Task.objects.create(
            owner=self.manager,
            project=self.project,
            assigned_to=self.employee,
            title="Assigned Task",
            description="Task assigned to employee",
            priority="medium",
            status="todo",
            estimated_hours=4,
            due_date=date.today(),
        )

        self.other_task = Task.objects.create(
            owner=self.manager,
            project=self.project,
            assigned_to=self.other_employee,
            title="Other Employee Task",
            description="Not assigned to employee",
            priority="low",
            status="todo",
            estimated_hours=2,
            due_date=date.today(),
        )

        self.unassigned_task = Task.objects.create(
            owner=self.manager,
            project=self.project,
            assigned_to=None,
            title="Unassigned Task",
            description="Task without assignment",
            priority="high",
            status="todo",
            estimated_hours=3,
            due_date=date.today(),
        )

        self.task_url = "/api/tasks/"
        self.assigned_task_url = (
            f"/api/tasks/{self.assigned_task.id}/"
        )

    # --------------------------------------------------
    # LIST
    # --------------------------------------------------

    def test_employee_lists_only_assigned_tasks(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            self.task_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        task_ids = [
            task["id"]
            for task in response.data
        ]

        self.assertIn(
            self.assigned_task.id,
            task_ids,
        )

        self.assertNotIn(
            self.other_task.id,
            task_ids,
        )

        self.assertNotIn(
            self.unassigned_task.id,
            task_ids,
        )

    def test_manager_lists_all_tasks(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.get(
            self.task_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        task_ids = [
            task["id"]
            for task in response.data
        ]

        self.assertIn(
            self.assigned_task.id,
            task_ids,
        )

        self.assertIn(
            self.other_task.id,
            task_ids,
        )

        self.assertIn(
            self.unassigned_task.id,
            task_ids,
        )

    def test_admin_lists_all_tasks(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            self.task_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        task_ids = [
            task["id"]
            for task in response.data
        ]

        self.assertIn(
            self.assigned_task.id,
            task_ids,
        )

        self.assertIn(
            self.other_task.id,
            task_ids,
        )

        self.assertIn(
            self.unassigned_task.id,
            task_ids,
        )

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------

    def test_employee_can_retrieve_assigned_task(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            self.assigned_task_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.assigned_task.id,
        )

    def test_employee_cannot_retrieve_other_employee_task(self):
        self.client.force_authenticate(
            user=self.employee
        )

        url = (
            f"/api/tasks/{self.other_task.id}/"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_employee_cannot_retrieve_unassigned_task(self):
        self.client.force_authenticate(
            user=self.employee
        )

        url = (
            f"/api/tasks/{self.unassigned_task.id}/"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------

    def test_manager_can_create_task(self):
        self.client.force_authenticate(
            user=self.manager
        )

        payload = {
            "project_id": self.project.id,
            "assigned_to_id": self.employee.id,
            "title": "New Manager Task",
            "description": "Created by manager",
            "priority": "high",
            "status": "todo",
            "estimated_hours": 5,
            "due_date": str(date.today()),
        }

        response = self.client.post(
            self.task_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Task.objects.filter(
                title="New Manager Task"
            ).exists()
        )

    def test_admin_can_create_task(self):
        self.client.force_authenticate(
            user=self.admin
        )

        payload = {
            "project_id": self.project.id,
            "assigned_to_id": self.employee.id,
            "title": "New Admin Task",
            "description": "Created by admin",
            "priority": "medium",
            "status": "todo",
            "estimated_hours": 3,
            "due_date": str(date.today()),
        }

        response = self.client.post(
            self.task_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_employee_cannot_create_task(self):
        self.client.force_authenticate(
            user=self.employee
        )

        payload = {
            "project_id": self.project.id,
            "title": "Unauthorized Task",
            "description": "Employee should not create",
            "priority": "medium",
            "status": "todo",
            "estimated_hours": 2,
            "due_date": str(date.today()),
        }

        response = self.client.post(
            self.task_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # --------------------------------------------------
    # MANAGER / ADMIN UPDATE
    # --------------------------------------------------

    def test_manager_can_update_task(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.patch(
            self.assigned_task_url,
            {
                "title": "Updated Task Title"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assigned_task.refresh_from_db()

        self.assertEqual(
            self.assigned_task.title,
            "Updated Task Title",
        )

    def test_admin_can_update_task(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.patch(
            self.assigned_task_url,
            {
                "title": "Admin Updated Title"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assigned_task.refresh_from_db()

        self.assertEqual(
            self.assigned_task.title,
            "Admin Updated Title",
        )

    # --------------------------------------------------
    # EMPLOYEE STATUS UPDATE
    # --------------------------------------------------

    def test_employee_can_update_status(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.patch(
            self.assigned_task_url,
            {
                "status": "in_progress"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assigned_task.refresh_from_db()

        self.assertEqual(
            self.assigned_task.status,
            "in_progress",
        )

        self.assertFalse(
            self.assigned_task.completed
        )

    def test_employee_can_complete_task(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.patch(
            self.assigned_task_url,
            {
                "status": "completed"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assigned_task.refresh_from_db()

        self.assertEqual(
            self.assigned_task.status,
            "completed",
        )

        self.assertTrue(
            self.assigned_task.completed
        )

    # --------------------------------------------------
    # EMPLOYEE RESTRICTIONS
    # --------------------------------------------------

    def test_employee_cannot_update_title(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.patch(
            self.assigned_task_url,
            {
                "title": "Unauthorized Title Change"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assigned_task.refresh_from_db()

        self.assertEqual(
            self.assigned_task.title,
            "Assigned Task",
        )

    def test_employee_cannot_change_project(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.patch(
            self.assigned_task_url,
            {
                "project_id": self.employee_project.id
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assigned_task.refresh_from_db()

        self.assertEqual(
            self.assigned_task.project_id,
            self.project.id,
        )

    def test_employee_cannot_reassign_task(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.patch(
            self.assigned_task_url,
            {
                "assigned_to_id": self.other_employee.id
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assigned_task.refresh_from_db()

        self.assertEqual(
            self.assigned_task.assigned_to_id,
            self.employee.id,
        )

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------

    def test_manager_can_delete_task(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.delete(
            self.assigned_task_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Task.objects.filter(
                id=self.assigned_task.id
            ).exists()
        )

    def test_admin_can_delete_task(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.delete(
            self.assigned_task_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Task.objects.filter(
                id=self.assigned_task.id
            ).exists()
        )

    def test_employee_cannot_delete_task(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.delete(
            self.assigned_task_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            Task.objects.filter(
                id=self.assigned_task.id
            ).exists()
        )

    # --------------------------------------------------
    # INVALID TASK
    # --------------------------------------------------

    def test_invalid_task_returns_404(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.get(
            "/api/tasks/999999/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # --------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------

    def test_unauthenticated_list_is_denied(self):
        response = self.client.get(
            self.task_url
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )
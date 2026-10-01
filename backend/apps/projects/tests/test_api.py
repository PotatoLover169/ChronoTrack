from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from apps.clients.models import Client
from apps.projects.models import Project


User = get_user_model()


class ProjectsAPITestCase(APITestCase):

    def setUp(self):
        # =====================================================
        # Users
        # =====================================================

        self.employee = User.objects.create_user(
            username="employee_project_test",
            email="employee_project@example.com",
            password="TestPass123!",
        )

        self.manager = User.objects.create_user(
            username="manager_project_test",
            email="manager_project@example.com",
            password="TestPass123!",
        )

        self.admin = User.objects.create_superuser(
            username="admin_project_test",
            email="admin_project@example.com",
            password="TestPass123!",
        )

        employee_group, _ = Group.objects.get_or_create(
            name="Employee"
        )

        manager_group, _ = Group.objects.get_or_create(
            name="Manager"
        )

        self.employee.groups.add(employee_group)
        self.manager.groups.add(manager_group)

        # =====================================================
        # Clients
        # =====================================================

        self.employee_client = Client.objects.create(
            owner=self.employee,
            name="Employee Client",
            company="Employee Company",
            email="employee-client@example.com",
        )

        self.manager_client = Client.objects.create(
            owner=self.manager,
            name="Manager Client",
            company="Manager Company",
            email="manager-client@example.com",
        )

        # =====================================================
        # Projects
        # =====================================================

        self.employee_project = Project.objects.create(
            owner=self.employee,
            client=self.employee_client,
            name="Employee Project",
            description="Employee-owned project.",
            status="in_progress",
            hourly_rate=500,
        )

        self.manager_project = Project.objects.create(
            owner=self.manager,
            client=self.manager_client,
            name="Manager Project",
            description="Manager-owned project.",
            status="planning",
            hourly_rate=750,
        )

        self.shared_project = Project.objects.create(
            owner=self.manager,
            client=self.manager_client,
            name="Shared Project",
            description="Project assigned to employee.",
            status="in_progress",
            hourly_rate=600,
        )

        self.shared_project.members.add(
            self.employee
        )

    # =========================================================
    # LIST
    # =========================================================

    def test_employee_can_list_accessible_projects(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            "/api/projects/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        project_names = [
            project["name"]
            for project in response.data
        ]

        self.assertIn(
            "Employee Project",
            project_names,
        )

        self.assertIn(
            "Shared Project",
            project_names,
        )

        self.assertNotIn(
            "Manager Project",
            project_names,
        )

    def test_manager_can_list_all_projects(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.get(
            "/api/projects/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        project_names = [
            project["name"]
            for project in response.data
        ]

        self.assertIn(
            "Employee Project",
            project_names,
        )

        self.assertIn(
            "Manager Project",
            project_names,
        )

        self.assertIn(
            "Shared Project",
            project_names,
        )

    def test_admin_can_list_all_projects(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            "/api/projects/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            3,
        )

    def test_unauthenticated_user_cannot_list_projects(self):
        response = self.client.get(
            "/api/projects/"
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    # =========================================================
    # CREATE
    # =========================================================

    def test_manager_can_create_project(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.post(
            "/api/projects/",
            {
                "client_id": self.manager_client.id,
                "name": "New Manager Project",
                "description": "Created through API.",
                "status": "planning",
                "hourly_rate": "800.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        project = Project.objects.get(
            name="New Manager Project"
        )

        self.assertEqual(
            project.owner,
            self.manager,
        )

        self.assertEqual(
            project.client,
            self.manager_client,
        )

    def test_admin_can_create_project(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            "/api/projects/",
            {
                "client_id": self.manager_client.id,
                "name": "New Admin Project",
                "description": "Created by admin.",
                "status": "planning",
                "hourly_rate": "900.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        project = Project.objects.get(
            name="New Admin Project"
        )

        self.assertEqual(
            project.owner,
            self.admin,
        )

    def test_employee_cannot_create_project(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.post(
            "/api/projects/",
            {
                "client_id": self.employee_client.id,
                "name": "Unauthorized Project",
                "description": "Should not be created.",
                "status": "planning",
                "hourly_rate": "500.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            Project.objects.filter(
                name="Unauthorized Project"
            ).exists()
        )

    # =========================================================
    # RETRIEVE
    # =========================================================

    def test_employee_can_retrieve_owned_project(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            f"/api/projects/{self.employee_project.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["name"],
            "Employee Project",
        )

    def test_employee_can_retrieve_member_project(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            f"/api/projects/{self.shared_project.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["name"],
            "Shared Project",
        )

    def test_employee_cannot_retrieve_inaccessible_project(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            f"/api/projects/{self.manager_project.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_manager_can_retrieve_any_project(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.get(
            f"/api/projects/{self.employee_project.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_admin_can_retrieve_any_project(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            f"/api/projects/{self.manager_project.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_invalid_project_returns_404(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.get(
            "/api/projects/999999/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # =========================================================
    # UPDATE
    # =========================================================

    def test_manager_can_update_project(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.patch(
            f"/api/projects/{self.manager_project.id}/",
            {
                "name": "Updated Manager Project",
                "status": "in_progress",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.manager_project.refresh_from_db()

        self.assertEqual(
            self.manager_project.name,
            "Updated Manager Project",
        )

        self.assertEqual(
            self.manager_project.status,
            "in_progress",
        )

    def test_admin_can_update_project(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.patch(
            f"/api/projects/{self.employee_project.id}/",
            {
                "name": "Admin Updated Project",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.employee_project.refresh_from_db()

        self.assertEqual(
            self.employee_project.name,
            "Admin Updated Project",
        )

    def test_employee_cannot_update_project(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.patch(
            f"/api/projects/{self.employee_project.id}/",
            {
                "name": "Unauthorized Update",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # =========================================================
    # DELETE
    # =========================================================

    def test_manager_can_delete_project(self):
        self.client.force_authenticate(
            user=self.manager
        )

        project_id = self.manager_project.id

        response = self.client.delete(
            f"/api/projects/{project_id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Project.objects.filter(
                id=project_id
            ).exists()
        )

    def test_admin_can_delete_project(self):
        self.client.force_authenticate(
            user=self.admin
        )

        project_id = self.employee_project.id

        response = self.client.delete(
            f"/api/projects/{project_id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Project.objects.filter(
                id=project_id
            ).exists()
        )

    def test_employee_cannot_delete_project(self):
        self.client.force_authenticate(
            user=self.employee
        )

        project_id = self.employee_project.id

        response = self.client.delete(
            f"/api/projects/{project_id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            Project.objects.filter(
                id=project_id
            ).exists()
        )
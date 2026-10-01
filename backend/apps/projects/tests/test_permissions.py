from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.projects.api.permissions import ProjectPermission


User = get_user_model()


class ProjectsPermissionTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        self.employee = User.objects.create_user(
            username="employee_project_permission",
            email="employee_permission@example.com",
            password="TestPass123!",
        )

        self.manager = User.objects.create_user(
            username="manager_project_permission",
            email="manager_permission@example.com",
            password="TestPass123!",
        )

        self.admin = User.objects.create_superuser(
            username="admin_project_permission",
            email="admin_permission@example.com",
            password="TestPass123!",
        )

        employee_group, _ = Group.objects.get_or_create(
            name="Employee"
        )

        manager_group, _ = Group.objects.get_or_create(
            name="Manager"
        )

        self.employee.groups.add(
            employee_group
        )

        self.manager.groups.add(
            manager_group
        )

        self.permission = ProjectPermission()

    # =========================================================
    # READ ACCESS
    # =========================================================

    def test_employee_can_view_projects(self):
        request = self.factory.get("/")

        request.user = self.employee

        self.assertTrue(
            self.permission.has_permission(
                request,
                None,
            )
        )

    def test_manager_can_view_projects(self):
        request = self.factory.get("/")

        request.user = self.manager

        self.assertTrue(
            self.permission.has_permission(
                request,
                None,
            )
        )

    def test_admin_can_view_projects(self):
        request = self.factory.get("/")

        request.user = self.admin

        self.assertTrue(
            self.permission.has_permission(
                request,
                None,
            )
        )

    # =========================================================
    # CREATE / UPDATE / DELETE
    # =========================================================

    def test_employee_cannot_modify_projects(self):
        for method in [
            self.factory.post,
            self.factory.put,
            self.factory.patch,
            self.factory.delete,
        ]:
            request = method("/")

            request.user = self.employee

            self.assertFalse(
                self.permission.has_permission(
                    request,
                    None,
                )
            )

    def test_manager_can_modify_projects(self):
        for method in [
            self.factory.post,
            self.factory.put,
            self.factory.patch,
            self.factory.delete,
        ]:
            request = method("/")

            request.user = self.manager

            self.assertTrue(
                self.permission.has_permission(
                    request,
                    None,
                )
            )

    def test_admin_can_modify_projects(self):
        for method in [
            self.factory.post,
            self.factory.put,
            self.factory.patch,
            self.factory.delete,
        ]:
            request = method("/")

            request.user = self.admin

            self.assertTrue(
                self.permission.has_permission(
                    request,
                    None,
                )
            )

    # =========================================================
    # ANONYMOUS
    # =========================================================

    def test_anonymous_user_cannot_access_projects(self):
        request = self.factory.get("/")

        request.user = None

        self.assertFalse(
            self.permission.has_permission(
                request,
                None,
            )
        )
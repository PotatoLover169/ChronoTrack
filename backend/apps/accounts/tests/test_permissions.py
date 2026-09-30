from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.accounts.api.permissions import (
    IsAdminUserRole,
    IsManagerOrAdminRole,
)


User = get_user_model()


class AccountsPermissionTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        self.employee = User.objects.create_user(
            username="employee_permission_test",
            email="employee_permission@example.com",
            password="TestPass123!",
        )

        self.manager = User.objects.create_user(
            username="manager_permission_test",
            email="manager_permission@example.com",
            password="TestPass123!",
        )

        self.admin = User.objects.create_superuser(
            username="admin_permission_test",
            email="admin_permission@example.com",
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

    # =========================================================
    # IsAdminUserRole
    # =========================================================

    def test_admin_is_allowed_by_admin_permission(self):
        request = self.factory.get("/")
        request.user = self.admin

        permission = IsAdminUserRole()

        self.assertTrue(
            permission.has_permission(request, None)
        )

    def test_manager_is_denied_by_admin_permission(self):
        request = self.factory.get("/")
        request.user = self.manager

        permission = IsAdminUserRole()

        self.assertFalse(
            permission.has_permission(request, None)
        )

    def test_employee_is_denied_by_admin_permission(self):
        request = self.factory.get("/")
        request.user = self.employee

        permission = IsAdminUserRole()

        self.assertFalse(
            permission.has_permission(request, None)
        )

    def test_anonymous_user_is_denied_by_admin_permission(self):
        request = self.factory.get("/")
        request.user = None

        permission = IsAdminUserRole()

        self.assertFalse(
            permission.has_permission(request, None)
        )

    # =========================================================
    # IsManagerOrAdminRole
    # =========================================================

    def test_admin_is_allowed_by_manager_or_admin_permission(self):
        request = self.factory.get("/")
        request.user = self.admin

        permission = IsManagerOrAdminRole()

        self.assertTrue(
            permission.has_permission(request, None)
        )

    def test_manager_is_allowed_by_manager_or_admin_permission(self):
        request = self.factory.get("/")
        request.user = self.manager

        permission = IsManagerOrAdminRole()

        self.assertTrue(
            permission.has_permission(request, None)
        )

    def test_employee_is_denied_by_manager_or_admin_permission(self):
        request = self.factory.get("/")
        request.user = self.employee

        permission = IsManagerOrAdminRole()

        self.assertFalse(
            permission.has_permission(request, None)
        )

    def test_anonymous_user_is_denied_by_manager_or_admin_permission(self):
        request = self.factory.get("/")
        request.user = None

        permission = IsManagerOrAdminRole()

        self.assertFalse(
            permission.has_permission(request, None)
        )
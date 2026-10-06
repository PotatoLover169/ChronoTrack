from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import RequestFactory, TestCase

from apps.approvals.permissions import (
    IsEmployee,
    IsManagerOrAdmin,
)


User = get_user_model()


class ApprovalsPermissionsTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.employee = User.objects.create_user(
            username="employee",
            email="employee@example.com",
            password="TestPass123!",
        )

        self.manager = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="TestPass123!",
        )

        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="TestPass123!",
        )

        self.admin_group, _ = Group.objects.get_or_create(
            name="Admin",
        )

        self.manager_group, _ = Group.objects.get_or_create(
            name="Manager",
        )

        self.manager.groups.add(
            self.manager_group,
        )

        self.admin.groups.add(
            self.admin_group,
        )

        self.admin.is_staff = False
        self.admin.save(
            update_fields=["is_staff"],
        )

    def test_authenticated_employee_has_employee_permission(self):
        request = self.factory.get("/")

        request.user = self.employee

        permission = IsEmployee()

        self.assertTrue(
            permission.has_permission(
                request,
                None,
            )
        )

    def test_unauthenticated_user_is_denied_employee_permission(self):
        request = self.factory.get("/")

        request.user = type(
            "AnonymousUser",
            (),
            {
                "is_authenticated": False,
            },
        )()

        permission = IsEmployee()

        self.assertFalse(
            permission.has_permission(
                request,
                None,
            )
        )

    def test_manager_has_manager_permission(self):
        request = self.factory.get("/")

        request.user = self.manager

        permission = IsManagerOrAdmin()

        self.assertTrue(
            permission.has_permission(
                request,
                None,
            )
        )

    def test_admin_group_has_manager_permission(self):
        request = self.factory.get("/")

        request.user = self.admin

        permission = IsManagerOrAdmin()

        self.assertTrue(
            permission.has_permission(
                request,
                None,
            )
        )

    def test_superuser_has_manager_permission(self):
        superuser = User.objects.create_superuser(
            username="superuser",
            email="superuser@example.com",
            password="TestPass123!",
        )

        request = self.factory.get("/")

        request.user = superuser

        permission = IsManagerOrAdmin()

        self.assertTrue(
            permission.has_permission(
                request,
                None,
            )
        )

    def test_employee_is_denied_manager_permission(self):
        request = self.factory.get("/")

        request.user = self.employee

        permission = IsManagerOrAdmin()

        self.assertFalse(
            permission.has_permission(
                request,
                None,
            )
        )

    def test_staff_flag_alone_does_not_grant_manager_permission(self):
        staff_user = User.objects.create_user(
            username="staffuser",
            email="staff@example.com",
            password="TestPass123!",
            is_staff=True,
        )

        request = self.factory.get("/")

        request.user = staff_user

        permission = IsManagerOrAdmin()

        self.assertFalse(
            permission.has_permission(
                request,
                None,
            )
        )
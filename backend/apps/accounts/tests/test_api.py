from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AccountsAPITestCase(APITestCase):

    def setUp(self):
        self.employee = User.objects.create_user(
            username="employee_test",
            email="employee@example.com",
            password="TestPass123!",
        )

        self.manager = User.objects.create_user(
            username="manager_test",
            email="manager@example.com",
            password="TestPass123!",
        )

        self.admin = User.objects.create_superuser(
            username="admin_test",
            email="admin@example.com",
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

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def test_user_can_register(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "new_user",
                "email": "new@example.com",
                "password": "NewPass123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            User.objects.filter(
                username="new_user"
            ).exists()
        )

    # ---------------------------------------------------------
    # Login
    # ---------------------------------------------------------

    def test_user_can_login(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "employee_test",
                "password": "TestPass123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_invalid_login_is_rejected(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "employee_test",
                "password": "WrongPassword!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ---------------------------------------------------------
    # Me
    # ---------------------------------------------------------

    def test_authenticated_user_can_view_me(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            "/api/auth/me/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["username"],
            "employee_test",
        )

        self.assertEqual(
            response.data["role"],
            "Employee",
        )

    def test_manager_role_is_returned_correctly(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.get(
            "/api/auth/me/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["role"],
            "Manager",
        )

    def test_admin_role_is_returned_correctly(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            "/api/auth/me/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["role"],
            "Admin",
        )

    # ---------------------------------------------------------
    # Profile
    # ---------------------------------------------------------

    def test_authenticated_user_can_update_profile(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.patch(
            "/api/auth/profile/",
            {
                "first_name": "Test",
                "last_name": "Employee",
                "email": "updated@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.employee.refresh_from_db()

        self.assertEqual(
            self.employee.first_name,
            "Test",
        )

        self.assertEqual(
            self.employee.last_name,
            "Employee",
        )

        self.assertEqual(
            self.employee.email,
            "updated@example.com",
        )

    # ---------------------------------------------------------
    # Admin user creation
    # ---------------------------------------------------------

    def test_admin_can_create_employee(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            "/api/auth/users/create/",
            {
                "username": "created_employee",
                "email": "created@example.com",
                "first_name": "Created",
                "last_name": "Employee",
                "password": "CreatedPass123!",
                "role": "Employee",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = User.objects.get(
            username="created_employee"
        )

        self.assertTrue(
            user.groups.filter(
                name="Employee"
            ).exists()
        )

    def test_admin_can_create_manager(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            "/api/auth/users/create/",
            {
                "username": "created_manager",
                "email": "manager@example.com",
                "first_name": "Created",
                "last_name": "Manager",
                "password": "CreatedPass123!",
                "role": "Manager",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = User.objects.get(
            username="created_manager"
        )

        self.assertTrue(
            user.groups.filter(
                name="Manager"
            ).exists()
        )

    def test_employee_cannot_create_users(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.post(
            "/api/auth/users/create/",
            {
                "username": "unauthorized_user",
                "email": "unauthorized@example.com",
                "password": "CreatedPass123!",
                "role": "Employee",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_manager_cannot_create_users(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.post(
            "/api/auth/users/create/",
            {
                "username": "unauthorized_manager",
                "email": "unauthorized@example.com",
                "password": "CreatedPass123!",
                "role": "Employee",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ---------------------------------------------------------
    # Admin user list
    # ---------------------------------------------------------

    def test_admin_can_list_users(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            "/api/auth/users/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_manager_cannot_list_all_users(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.get(
            "/api/auth/users/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_employee_cannot_list_all_users(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            "/api/auth/users/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ---------------------------------------------------------
    # Assignable users
    # ---------------------------------------------------------

    def test_manager_can_list_assignable_employees(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.get(
            "/api/auth/users/assignable/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        usernames = [
            user["username"]
            for user in response.data
        ]

        self.assertIn(
            "employee_test",
            usernames,
        )

    def test_admin_can_list_assignable_employees(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            "/api/auth/users/assignable/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_employee_cannot_list_assignable_users(self):
        self.client.force_authenticate(
            user=self.employee
        )

        response = self.client.get(
            "/api/auth/users/assignable/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
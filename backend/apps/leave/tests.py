from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import LeaveBalance, LeaveRequest, LeaveType


User = get_user_model()


class LeaveAPITestCase(TestCase):
    """
    Automated API tests for the ChronoTrack Leave module.

    Covers:
    - leave request creation
    - validation errors
    - duplicate pending requests
    - leave approval
    - leave rejection
    - leave balance deduction
    - leave request cancellation
    - role-based access
    """

    def setUp(self):
        self.client = APIClient()

        # ---------------------------------------------------------
        # Users
        # ---------------------------------------------------------
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

        # ---------------------------------------------------------
        # Roles
        # ---------------------------------------------------------
        employee_group, _ = Group.objects.get_or_create(
            name="Employee"
        )

        manager_group, _ = Group.objects.get_or_create(
            name="Manager"
        )

        self.employee.groups.add(employee_group)
        self.manager.groups.add(manager_group)

        # ---------------------------------------------------------
        # Leave type
        # ---------------------------------------------------------
        self.leave_type = LeaveType.objects.create(
            name="Vacation Leave",
            description="Annual vacation leave.",
            default_days="15.00",
            is_paid=True,
            is_active=True,
        )

        # ---------------------------------------------------------
        # Employee balance
        # ---------------------------------------------------------
        self.balance = LeaveBalance.objects.create(
            employee=self.employee,
            leave_type=self.leave_type,
            year=2026,
            allocated_days="10.00",
            used_days="0.00",
        )

    # =============================================================
    # Helpers
    # =============================================================

    def authenticate_as(self, user):
        self.client.force_authenticate(user=user)

    def create_leave_request(
        self,
        start_date="2026-10-10",
        end_date="2026-10-11",
        reason="Test leave",
    ):
        return self.client.post(
            "/api/leave/requests/create/",
            {
                "leave_type": self.leave_type.id,
                "start_date": start_date,
                "end_date": end_date,
                "reason": reason,
            },
            format="json",
        )

    # =============================================================
    # Creation
    # =============================================================

    def test_employee_can_create_leave_request(self):
        self.authenticate_as(self.employee)

        response = self.create_leave_request()

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            LeaveRequest.objects.filter(
                id=response.data["id"]
            ).exists()
        )

    def test_employee_cannot_create_leave_with_invalid_dates(self):
        self.authenticate_as(self.employee)

        response = self.create_leave_request(
            start_date="2026-10-15",
            end_date="2026-10-10",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_employee_cannot_create_duplicate_pending_request(self):
        self.authenticate_as(self.employee)

        first_response = self.create_leave_request()

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        second_response = self.create_leave_request(
            start_date="2026-10-10",
            end_date="2026-10-11",
            reason="Duplicate request",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_employee_cannot_create_leave_without_sufficient_balance(self):
        self.authenticate_as(self.employee)

        response = self.create_leave_request(
            start_date="2026-10-10",
            end_date="2026-10-25",
            reason="Too many days",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # =============================================================
    # Employee request access
    # =============================================================

    def test_employee_can_view_own_leave_requests(self):
        self.authenticate_as(self.employee)

        self.create_leave_request()

        response = self.client.get(
            "/api/leave/requests/my/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_employee_cannot_access_manager_leave_list(self):
        self.authenticate_as(self.employee)

        response = self.client.get(
            "/api/leave/requests/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # =============================================================
    # Cancellation
    # =============================================================

    def test_employee_can_cancel_pending_leave_request(self):
        self.authenticate_as(self.employee)

        create_response = self.create_leave_request()

        self.assertEqual(
            create_response.status_code,
            status.HTTP_201_CREATED,
        )

        request_id = create_response.data["id"]

        cancel_response = self.client.patch(
            f"/api/leave/requests/{request_id}/cancel/",
            {},
            format="json",
        )

        self.assertEqual(
            cancel_response.status_code,
            status.HTTP_200_OK,
        )

        leave_request = LeaveRequest.objects.get(
            id=request_id
        )

        self.assertEqual(
            leave_request.status,
            "cancelled",
        )

        self.assertIsNotNone(
            leave_request.cancelled_at
        )

    def test_cancelling_pending_request_does_not_deduct_balance(self):
        self.authenticate_as(self.employee)

        create_response = self.create_leave_request()

        request_id = create_response.data["id"]

        cancel_response = self.client.patch(
            f"/api/leave/requests/{request_id}/cancel/",
            {},
            format="json",
        )

        self.assertEqual(
            cancel_response.status_code,
            status.HTTP_200_OK,
        )

        balance = LeaveBalance.objects.get(
            id=self.balance.id
        )

        self.assertEqual(
            balance.used_days,
            0,
        )

    # =============================================================
    # Approval
    # =============================================================

    def test_manager_can_approve_leave_request(self):
        self.authenticate_as(self.employee)

        create_response = self.create_leave_request()

        self.assertEqual(
            create_response.status_code,
            status.HTTP_201_CREATED,
        )

        request_id = create_response.data["id"]

        self.authenticate_as(self.manager)

        approve_response = self.client.patch(
            f"/api/leave/requests/{request_id}/approve/",
            {
                "manager_comment": "Approved for testing.",
            },
            format="json",
        )

        self.assertEqual(
            approve_response.status_code,
            status.HTTP_200_OK,
        )

        leave_request = LeaveRequest.objects.get(
            id=request_id
        )

        self.assertEqual(
            leave_request.status,
            "approved",
        )

        self.assertEqual(
            leave_request.reviewed_by,
            self.manager,
        )

        self.assertEqual(
            leave_request.manager_comment,
            "Approved for testing.",
        )

        self.assertIsNotNone(
            leave_request.reviewed_at
        )

    def test_approval_deducts_leave_balance(self):
        self.authenticate_as(self.employee)

        create_response = self.create_leave_request()

        request_id = create_response.data["id"]

        self.authenticate_as(self.manager)

        approve_response = self.client.patch(
            f"/api/leave/requests/{request_id}/approve/",
            {
                "manager_comment": "Approved.",
            },
            format="json",
        )

        self.assertEqual(
            approve_response.status_code,
            status.HTTP_200_OK,
        )

        balance = LeaveBalance.objects.get(
            id=self.balance.id
        )

        # 2-day request
        self.assertEqual(
            balance.used_days,
            2,
        )

        self.assertEqual(
            balance.remaining_days,
            8,
        )

    # =============================================================
    # Rejection
    # =============================================================

    def test_manager_can_reject_leave_request(self):
        self.authenticate_as(self.employee)

        create_response = self.create_leave_request()

        request_id = create_response.data["id"]

        self.authenticate_as(self.manager)

        reject_response = self.client.patch(
            f"/api/leave/requests/{request_id}/reject/",
            {
                "manager_comment": "Rejected for testing.",
            },
            format="json",
        )

        self.assertEqual(
            reject_response.status_code,
            status.HTTP_200_OK,
        )

        leave_request = LeaveRequest.objects.get(
            id=request_id
        )

        self.assertEqual(
            leave_request.status,
            "rejected",
        )

        self.assertEqual(
            leave_request.reviewed_by,
            self.manager,
        )

        self.assertEqual(
            leave_request.manager_comment,
            "Rejected for testing.",
        )

        self.assertIsNotNone(
            leave_request.reviewed_at
        )

    def test_rejection_does_not_deduct_leave_balance(self):
        self.authenticate_as(self.employee)

        create_response = self.create_leave_request()

        request_id = create_response.data["id"]

        self.authenticate_as(self.manager)

        reject_response = self.client.patch(
            f"/api/leave/requests/{request_id}/reject/",
            {
                "manager_comment": "Rejected.",
            },
            format="json",
        )

        self.assertEqual(
            reject_response.status_code,
            status.HTTP_200_OK,
        )

        balance = LeaveBalance.objects.get(
            id=self.balance.id
        )

        self.assertEqual(
            balance.used_days,
            0,
        )

    # =============================================================
    # Role permissions
    # =============================================================

    def test_manager_can_view_pending_leave_requests(self):
        self.authenticate_as(self.manager)

        response = self.client.get(
            "/api/leave/requests/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_admin_can_view_pending_leave_requests(self):
        self.authenticate_as(self.admin)

        response = self.client.get(
            "/api/leave/requests/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
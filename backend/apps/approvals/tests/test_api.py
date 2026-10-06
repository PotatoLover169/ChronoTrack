from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.approvals.models import (
    EditRequestStatus,
    TimeEntryEditRequest,
)
from apps.clients.models import Client
from apps.projects.models import Project
from apps.tracker.models import TimeEntry, TimeEntryStatus


User = get_user_model()


class ApprovalsAPITestCase(APITestCase):

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
            name="Manager",
        )

        self.manager.groups.add(
            manager_group,
        )

        self.client_record = Client.objects.create(
            owner=self.manager,
            name="Approval Client",
            company="Approval Company",
        )

        self.project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Approval Project",
            description="Approval API project",
            status="in_progress",
            hourly_rate=500,
        )

        self.other_project = Project.objects.create(
            owner=self.manager,
            client=self.client_record,
            name="Other Approval Project",
            description="Other approval API project",
            status="in_progress",
            hourly_rate=600,
        )

        start_time = timezone.now() - timedelta(
            hours=2,
        )

        self.time_entry = TimeEntry.objects.create(
            owner=self.employee,
            project=self.project,
            description="Original description",
            start_time=start_time,
            end_time=start_time + timedelta(hours=2),
            duration=timedelta(hours=2),
            billable=True,
            hourly_rate=Decimal("500.00"),
            status=TimeEntryStatus.COMPLETED,
        )

    def create_edit_request(self, user=None):
        if user is None:
            user = self.employee

        return TimeEntryEditRequest.objects.create(
            time_entry=self.time_entry,
            requested_by=user,
            requested_description="Corrected description",
            requested_billable=False,
            reason="Correcting the time entry.",
            status=EditRequestStatus.PENDING,
        )

    # --------------------------------------------------
    # EMPLOYEE
    # --------------------------------------------------

    def test_employee_can_create_edit_request(self):
        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.post(
            reverse(
                "create-time-entry-edit-request",
            ),
            {
                "time_entry": self.time_entry.id,
                "requested_description": (
                    "Corrected description"
                ),
                "requested_billable": False,
                "reason": (
                    "The original entry was incorrect."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            TimeEntryEditRequest.objects.count(),
            1,
        )

        edit_request = (
            TimeEntryEditRequest.objects.first()
        )

        self.assertEqual(
            edit_request.requested_by,
            self.employee,
        )

        self.assertEqual(
            edit_request.status,
            EditRequestStatus.PENDING,
        )

    def test_employee_can_view_own_requests(self):
        edit_request = self.create_edit_request()

        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            reverse(
                "my-time-entry-edit-requests",
            ),
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
            response.data[0]["id"],
            edit_request.id,
        )

    def test_employee_cannot_view_other_users_requests(self):
        self.create_edit_request(
            user=self.other_employee,
        )

        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            reverse(
                "my-time-entry-edit-requests",
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            0,
        )

    def test_employee_can_cancel_own_pending_request(self):
        edit_request = self.create_edit_request()

        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.patch(
            reverse(
                "cancel-time-entry-edit-request",
                kwargs={
                    "pk": edit_request.id,
                },
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        edit_request.refresh_from_db()

        self.assertEqual(
            edit_request.status,
            EditRequestStatus.CANCELLED,
        )

    def test_employee_cannot_cancel_another_users_request(self):
        edit_request = self.create_edit_request(
            user=self.other_employee,
        )

        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.patch(
            reverse(
                "cancel-time-entry-edit-request",
                kwargs={
                    "pk": edit_request.id,
                },
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # --------------------------------------------------
    # MANAGER
    # --------------------------------------------------

    def test_manager_can_view_pending_requests(self):
        self.create_edit_request()

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            reverse(
                "pending-time-entry-edit-requests",
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_manager_can_view_request_detail(self):
        edit_request = self.create_edit_request()

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            reverse(
                "time-entry-edit-request-detail",
                kwargs={
                    "pk": edit_request.id,
                },
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            edit_request.id,
        )

    def test_manager_can_approve_request(self):
        edit_request = self.create_edit_request()

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.patch(
            reverse(
                "approve-time-entry-edit-request",
                kwargs={
                    "pk": edit_request.id,
                },
            ),
            {
                "manager_comment": (
                    "Approved after review."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        edit_request.refresh_from_db()

        self.assertEqual(
            edit_request.status,
            EditRequestStatus.APPROVED,
        )

        self.assertEqual(
            edit_request.reviewed_by,
            self.manager,
        )

    def test_manager_can_reject_request(self):
        edit_request = self.create_edit_request()

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.patch(
            reverse(
                "reject-time-entry-edit-request",
                kwargs={
                    "pk": edit_request.id,
                },
            ),
            {
                "manager_comment": (
                    "The requested change cannot be verified."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        edit_request.refresh_from_db()

        self.assertEqual(
            edit_request.status,
            EditRequestStatus.REJECTED,
        )

        self.assertEqual(
            edit_request.reviewed_by,
            self.manager,
        )

    def test_manager_cannot_reject_without_comment(self):
        edit_request = self.create_edit_request()

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.patch(
            reverse(
                "reject-time-entry-edit-request",
                kwargs={
                    "pk": edit_request.id,
                },
            ),
            {
                "manager_comment": "",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        edit_request.refresh_from_db()

        self.assertEqual(
            edit_request.status,
            EditRequestStatus.PENDING,
        )

    def test_manager_cannot_approve_already_reviewed_request(
        self,
    ):
        edit_request = self.create_edit_request()

        edit_request.status = (
            EditRequestStatus.REJECTED
        )

        edit_request.save(
            update_fields=["status"],
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.patch(
            reverse(
                "approve-time-entry-edit-request",
                kwargs={
                    "pk": edit_request.id,
                },
            ),
            {
                "manager_comment": (
                    "Trying to approve again."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

    # --------------------------------------------------
    # ADMIN
    # --------------------------------------------------

    def test_admin_can_view_pending_requests(self):
        self.create_edit_request()

        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.get(
            reverse(
                "pending-time-entry-edit-requests",
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_admin_can_approve_request(self):
        edit_request = self.create_edit_request()

        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.patch(
            reverse(
                "approve-time-entry-edit-request",
                kwargs={
                    "pk": edit_request.id,
                },
            ),
            {
                "manager_comment": (
                    "Approved by administrator."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        edit_request.refresh_from_db()

        self.assertEqual(
            edit_request.status,
            EditRequestStatus.APPROVED,
        )

        self.assertEqual(
            edit_request.reviewed_by,
            self.admin,
        )

    # --------------------------------------------------
    # EMPLOYEE RESTRICTIONS
    # --------------------------------------------------

    def test_employee_cannot_view_pending_requests(self):
        self.create_edit_request()

        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            reverse(
                "pending-time-entry-edit-requests",
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_employee_cannot_view_request_detail(self):
        edit_request = self.create_edit_request()

        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.get(
            reverse(
                "time-entry-edit-request-detail",
                kwargs={
                    "pk": edit_request.id,
                },
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_employee_cannot_approve_request(self):
        edit_request = self.create_edit_request()

        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.patch(
            reverse(
                "approve-time-entry-edit-request",
                kwargs={
                    "pk": edit_request.id,
                },
            ),
            {
                "manager_comment": (
                    "Unauthorized approval."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_employee_cannot_reject_request(self):
        edit_request = self.create_edit_request()

        self.client.force_authenticate(
            user=self.employee,
        )

        response = self.client.patch(
            reverse(
                "reject-time-entry-edit-request",
                kwargs={
                    "pk": edit_request.id,
                },
            ),
            {
                "manager_comment": (
                    "Unauthorized rejection."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # --------------------------------------------------
    # UNAUTHENTICATED
    # --------------------------------------------------

    def test_unauthenticated_user_cannot_create_request(self):
        response = self.client.post(
            reverse(
                "create-time-entry-edit-request",
            ),
            {
                "time_entry": self.time_entry.id,
                "reason": "Unauthenticated request.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unauthenticated_user_cannot_view_pending_requests(
        self,
    ):
        response = self.client.get(
            reverse(
                "pending-time-entry-edit-requests",
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
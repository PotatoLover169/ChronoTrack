from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.approvals.exceptions import (
    EditRequestAlreadyReviewedError,
    PendingEditRequestExistsError,
)
from apps.approvals.models import EditRequestStatus
from apps.approvals.services import (
    approve_edit_request,
    cancel_edit_request,
    create_edit_request,
    reject_edit_request,
)
from apps.clients.models import Client
from apps.projects.models import Project
from apps.tracker.models import TimeEntry


User = get_user_model()


class ApprovalsServicesTestCase(TestCase):

    def setUp(self):
        # ---------------------------------------
        # Users
        # ---------------------------------------

        self.employee = User.objects.create_user(
            username="employee",
            email="employee@example.com",
            password="password123",
        )

        self.other_employee = User.objects.create_user(
            username="other_employee",
            email="other@example.com",
            password="password123",
        )

        self.manager = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="password123",
        )

        manager_group, _ = Group.objects.get_or_create(
            name="Manager"
        )

        self.manager.groups.add(manager_group)

        # ---------------------------------------
        # Client
        # ---------------------------------------

        self.client = Client.objects.create(
            owner=self.manager,
            name="Test Client",
            company="Test Company",
            email="client@example.com",
            phone="123456789",
            notes="Approval service test client",
        )

        # ---------------------------------------
        # Projects
        # ---------------------------------------

        self.project = Project.objects.create(
            owner=self.manager,
            client=self.client,
            name="Test Project",
            description="Project used for approval service tests.",
            status="in_progress",
            hourly_rate=500,
        )

        self.project.members.add(
            self.employee
        )

        self.second_project = Project.objects.create(
            owner=self.manager,
            client=self.client,
            name="Second Test Project",
            description="Second project used for approval tests.",
            status="in_progress",
            hourly_rate=600,
        )

        self.second_project.members.add(
            self.employee
        )

        # ---------------------------------------
        # Time Entry
        # ---------------------------------------

        self.start_time = (
            timezone.now() - timedelta(hours=3)
        )

        self.end_time = (
            timezone.now() - timedelta(hours=1)
        )

        self.time_entry = TimeEntry.objects.create(
            owner=self.employee,
            project=self.project,
            description="Original description",
            start_time=self.start_time,
            end_time=self.end_time,
            duration=timedelta(hours=2),
            billable=True,
            hourly_rate=Decimal("500.00"),
            status="completed",
        )

    # =====================================================
    # Helper
    # =====================================================

    def create_request(self, **overrides):
        data = {
            "time_entry": self.time_entry,
            "user": self.employee,
            "requested_project": self.project,
            "requested_task": None,
            "requested_start_time": (
                self.start_time + timedelta(minutes=10)
            ),
            "requested_end_time": (
                self.end_time + timedelta(minutes=10)
            ),
            "requested_description": "Updated description",
            "requested_billable": False,
            "reason": (
                "I entered the wrong time information."
            ),
        }

        data.update(overrides)

        with patch(
            "apps.approvals.services.notify_edit_request_submitted"
        ):
            return create_edit_request(**data)

    # =====================================================
    # CREATE
    # =====================================================

    @patch(
        "apps.approvals.services.notify_edit_request_submitted"
    )
    def test_create_edit_request(
        self,
        mock_notification,
    ):
        edit_request = create_edit_request(
            time_entry=self.time_entry,
            user=self.employee,
            requested_project=self.project,
            requested_task=None,
            requested_start_time=(
                self.start_time
                + timedelta(minutes=10)
            ),
            requested_end_time=(
                self.end_time
                + timedelta(minutes=10)
            ),
            requested_description="Incorrect time entry.",
            requested_billable=False,
            reason="Incorrect time entry.",
        )

        self.assertIsNotNone(
            edit_request.pk
        )

        self.assertEqual(
            edit_request.status,
            EditRequestStatus.PENDING,
        )

        self.assertEqual(
            edit_request.requested_by,
            self.employee,
        )

        self.assertEqual(
            edit_request.time_entry,
            self.time_entry,
        )

        self.assertEqual(
            edit_request.reason,
            "Incorrect time entry.",
        )

        mock_notification.assert_called_once()

    def test_cannot_create_duplicate_pending_request(
        self,
    ):
        self.create_request()

        with self.assertRaises(
            PendingEditRequestExistsError
        ):
            self.create_request()

    @patch(
        "apps.approvals.services.notify_edit_request_approved"
    )
    def test_can_create_new_request_after_previous_request_reviewed(
        self,
        mock_notification,
    ):
        first_request = self.create_request()

        approve_edit_request(
            edit_request=first_request,
            manager=self.manager,
            manager_comment="Approved.",
        )

        second_request = self.create_request(
            requested_description=(
                "Second correction request."
            )
        )

        self.assertIsNotNone(
            second_request.pk
        )

        self.assertEqual(
            second_request.status,
            EditRequestStatus.PENDING,
        )

        mock_notification.assert_called_once()

    # =====================================================
    # APPROVE
    # =====================================================

    @patch(
        "apps.approvals.services.notify_edit_request_approved"
    )
    def test_approve_updates_time_entry(
        self,
        mock_notification,
    ):
        edit_request = self.create_request()

        new_start = (
            self.start_time
            + timedelta(minutes=30)
        )

        new_end = (
            self.end_time
            + timedelta(minutes=30)
        )

        edit_request.requested_start_time = new_start
        edit_request.requested_end_time = new_end
        edit_request.requested_description = (
            "Corrected description"
        )
        edit_request.requested_billable = False

        edit_request.save()

        approve_edit_request(
            edit_request=edit_request,
            manager=self.manager,
            manager_comment=(
                "Approved after verification."
            ),
        )

        self.time_entry.refresh_from_db()
        edit_request.refresh_from_db()

        self.assertEqual(
            self.time_entry.start_time,
            new_start,
        )

        self.assertEqual(
            self.time_entry.end_time,
            new_end,
        )

        self.assertEqual(
            self.time_entry.description,
            "Corrected description",
        )

        self.assertFalse(
            self.time_entry.billable
        )

        self.assertEqual(
            self.time_entry.duration,
            new_end - new_start,
        )

        self.assertEqual(
            edit_request.status,
            EditRequestStatus.APPROVED,
        )

        self.assertEqual(
            edit_request.reviewed_by,
            self.manager,
        )

        self.assertEqual(
            edit_request.manager_comment,
            "Approved after verification.",
        )

        self.assertIsNotNone(
            edit_request.reviewed_at
        )

        mock_notification.assert_called_once()

    @patch(
        "apps.approvals.services.notify_edit_request_approved"
    )
    def test_approve_can_change_project(
        self,
        mock_notification,
    ):
        edit_request = self.create_request(
            requested_project=self.second_project,
        )

        approve_edit_request(
            edit_request=edit_request,
            manager=self.manager,
            manager_comment="Project corrected.",
        )

        self.time_entry.refresh_from_db()
        edit_request.refresh_from_db()

        self.assertEqual(
            self.time_entry.project,
            self.second_project,
        )

        self.assertEqual(
            edit_request.status,
            EditRequestStatus.APPROVED,
        )

        mock_notification.assert_called_once()

    @patch(
        "apps.approvals.services.notify_edit_request_approved"
    )
    def test_cannot_approve_already_reviewed_request(
        self,
        mock_notification,
    ):
        edit_request = self.create_request()

        approve_edit_request(
            edit_request=edit_request,
            manager=self.manager,
            manager_comment="Approved.",
        )

        with self.assertRaises(
            EditRequestAlreadyReviewedError
        ):
            approve_edit_request(
                edit_request=edit_request,
                manager=self.manager,
                manager_comment="Trying again.",
            )

        mock_notification.assert_called_once()

    # =====================================================
    # REJECT
    # =====================================================

    @patch(
        "apps.approvals.services.notify_edit_request_rejected"
    )
    def test_reject_edit_request(
        self,
        mock_notification,
    ):
        edit_request = self.create_request()

        reject_edit_request(
            edit_request=edit_request,
            manager=self.manager,
            manager_comment=(
                "The requested correction cannot be verified."
            ),
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

        self.assertEqual(
            edit_request.manager_comment,
            "The requested correction cannot be verified.",
        )

        self.assertIsNotNone(
            edit_request.reviewed_at
        )

        mock_notification.assert_called_once()

    def test_reject_requires_manager_comment(
        self,
    ):
        edit_request = self.create_request()

        with self.assertRaises(
            ValueError
        ):
            reject_edit_request(
                edit_request=edit_request,
                manager=self.manager,
                manager_comment="",
            )

        edit_request.refresh_from_db()

        self.assertEqual(
            edit_request.status,
            EditRequestStatus.PENDING,
        )

    @patch(
        "apps.approvals.services.notify_edit_request_rejected"
    )
    def test_cannot_reject_already_reviewed_request(
        self,
        mock_notification,
    ):
        edit_request = self.create_request()

        reject_edit_request(
            edit_request=edit_request,
            manager=self.manager,
            manager_comment="Rejected.",
        )

        with self.assertRaises(
            ValueError
        ):
            reject_edit_request(
                edit_request=edit_request,
                manager=self.manager,
                manager_comment="Trying again.",
            )

        mock_notification.assert_called_once()

    # =====================================================
    # CANCEL
    # =====================================================

    def test_cancel_own_pending_request(
        self,
    ):
        edit_request = self.create_request()

        cancel_edit_request(
            edit_request=edit_request,
            user=self.employee,
        )

        edit_request.refresh_from_db()

        self.assertEqual(
            edit_request.status,
            EditRequestStatus.CANCELLED,
        )

    def test_cannot_cancel_another_users_request(
        self,
    ):
        edit_request = self.create_request()

        with self.assertRaises(
            ValueError
        ):
            cancel_edit_request(
                edit_request=edit_request,
                user=self.other_employee,
            )

        edit_request.refresh_from_db()

        self.assertEqual(
            edit_request.status,
            EditRequestStatus.PENDING,
        )

    @patch(
        "apps.approvals.services.notify_edit_request_approved"
    )
    def test_cannot_cancel_reviewed_request(
        self,
        mock_notification,
    ):
        edit_request = self.create_request()

        approve_edit_request(
            edit_request=edit_request,
            manager=self.manager,
            manager_comment="Approved.",
        )

        with self.assertRaises(
            ValueError
        ):
            cancel_edit_request(
                edit_request=edit_request,
                user=self.employee,
            )

        mock_notification.assert_called_once()

        edit_request.refresh_from_db()

        self.assertEqual(
            edit_request.status,
            EditRequestStatus.APPROVED,
        )
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.approvals.models import (
    EditRequestStatus,
    TimeEntryEditRequest,
)
from apps.clients.models import Client
from apps.notifications.models import Notification
from apps.notifications.services import (
    create_notification,
    get_notifications,
    get_unread_notifications,
    mark_all_notifications_as_read,
    mark_notification_as_read,
    notify_edit_request_approved,
    notify_edit_request_rejected,
    notify_edit_request_submitted,
    notify_project_completed,
    notify_project_created,
    notify_task_completed,
    notify_task_created,
    notify_time_entry_deleted,
    notify_time_entry_updated,
    notify_timer_started,
    notify_timer_stopped,
)
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.tracker.models import (
    TimeEntry,
    TimeEntryStatus,
)


User = get_user_model()


class NotificationServicesTestCase(TestCase):

    def setUp(self):
        # ---------------------------------------
        # Users
        # ---------------------------------------

        self.user = User.objects.create_user(
            username="employee",
            email="employee@example.com",
            password="password123",
        )

        self.other_user = User.objects.create_user(
            username="other_employee",
            email="other@example.com",
            password="password123",
        )

        # ---------------------------------------
        # Client
        # ---------------------------------------

        self.client = Client.objects.create(
            owner=self.user,
            name="Test Client",
            company="Test Company",
            email="client@example.com",
            phone="123456789",
            notes="Notification test client",
        )

        # ---------------------------------------
        # Project
        # ---------------------------------------

        self.project = Project.objects.create(
            owner=self.user,
            client=self.client,
            name="Test Project",
            description="Notification test project.",
            status="in_progress",
            hourly_rate=500,
        )

        self.project.members.add(
            self.user
        )

        # ---------------------------------------
        # Task
        # ---------------------------------------

        self.task = Task.objects.create(
            owner=self.user,
            assigned_to=self.user,
            project=self.project,
            title="Test Task",
            description="Notification test task.",
            priority="medium",
            status="todo",
            estimated_hours=5,
            actual_hours=0,
        )

        # ---------------------------------------
        # Time Entry
        # ---------------------------------------

        self.start_time = (
            timezone.now() - timedelta(hours=2)
        )

        self.end_time = timezone.now()

        self.time_entry = TimeEntry.objects.create(
            owner=self.user,
            project=self.project,
            task=self.task,
            description="Test time entry",
            start_time=self.start_time,
            end_time=self.end_time,
            billable=True,
            hourly_rate=Decimal("500.00"),
            status=TimeEntryStatus.COMPLETED,
        )

        # ---------------------------------------
        # Approval Request
        # ---------------------------------------

        self.edit_request = (
            TimeEntryEditRequest.objects.create(
                time_entry=self.time_entry,
                requested_by=self.user,
                requested_project=self.project,
                requested_task=self.task,
                requested_start_time=self.start_time,
                requested_end_time=self.end_time,
                requested_description="Corrected description",
                requested_billable=True,
                reason="Incorrect time entry.",
                status=EditRequestStatus.PENDING,
            )
        )

    # =====================================================
    # GENERIC CREATION
    # =====================================================

    def test_create_notification(self):
        notification = create_notification(
            recipient=self.user,
            notification_type="system",
            title="Test Notification",
            message="This is a test notification.",
        )

        self.assertIsNotNone(
            notification.pk
        )

        self.assertEqual(
            notification.recipient,
            self.user,
        )

        self.assertEqual(
            notification.notification_type,
            "system",
        )

        self.assertEqual(
            notification.title,
            "Test Notification",
        )

        self.assertEqual(
            notification.message,
            "This is a test notification.",
        )

        self.assertFalse(
            notification.is_read
        )

    # =====================================================
    # TASK NOTIFICATIONS
    # =====================================================

    def test_notify_task_created(self):
        notification = notify_task_created(
            recipient=self.user,
            task=self.task,
        )

        self.assertEqual(
            notification.notification_type,
            "task",
        )

        self.assertEqual(
            notification.title,
            "New Task Created",
        )

        self.assertEqual(
            notification.message,
            "Test Task has been created successfully.",
        )

    def test_notify_task_completed(self):
        notification = notify_task_completed(
            recipient=self.user,
            task=self.task,
        )

        self.assertEqual(
            notification.notification_type,
            "task",
        )

        self.assertEqual(
            notification.title,
            "Task Completed",
        )

        self.assertEqual(
            notification.message,
            "Test Task has been completed.",
        )

    # =====================================================
    # PROJECT NOTIFICATIONS
    # =====================================================

    def test_notify_project_created(self):
        notification = notify_project_created(
            recipient=self.user,
            project=self.project,
        )

        self.assertEqual(
            notification.notification_type,
            "project",
        )

        self.assertEqual(
            notification.title,
            "New Project Created",
        )

        self.assertEqual(
            notification.message,
            "Test Project has been created successfully.",
        )

    def test_notify_project_completed(self):
        notification = notify_project_completed(
            recipient=self.user,
            project=self.project,
        )

        self.assertEqual(
            notification.notification_type,
            "project",
        )

        self.assertEqual(
            notification.title,
            "Project Completed",
        )

        self.assertEqual(
            notification.message,
            "Test Project has been completed.",
        )

    # =====================================================
    # TRACKER NOTIFICATIONS
    # =====================================================

    def test_notify_timer_started(self):
        notification = notify_timer_started(
            recipient=self.user,
            time_entry=self.time_entry,
        )

        self.assertEqual(
            notification.notification_type,
            "tracker",
        )

        self.assertEqual(
            notification.title,
            "Timer Started",
        )

        self.assertEqual(
            notification.message,
            "Timer started for Test Project.",
        )

    def test_notify_timer_stopped(self):
        notification = notify_timer_stopped(
            recipient=self.user,
            time_entry=self.time_entry,
        )

        self.assertEqual(
            notification.notification_type,
            "tracker",
        )

        self.assertEqual(
            notification.title,
            "Timer Stopped",
        )

        self.assertEqual(
            notification.message,
            "Timer stopped for Test Project.",
        )

    def test_notify_time_entry_updated(self):
        notification = notify_time_entry_updated(
            recipient=self.user,
            time_entry=self.time_entry,
        )

        self.assertEqual(
            notification.notification_type,
            "tracker",
        )

        self.assertEqual(
            notification.title,
            "Time Entry Updated",
        )

        self.assertEqual(
            notification.message,
            "Time entry for Test Project has been updated.",
        )

    def test_notify_time_entry_deleted(self):
        notification = notify_time_entry_deleted(
            recipient=self.user,
            time_entry=self.time_entry,
        )

        self.assertEqual(
            notification.notification_type,
            "tracker",
        )

        self.assertEqual(
            notification.title,
            "Time Entry Deleted",
        )

        self.assertEqual(
            notification.message,
            "Time entry for Test Project has been deleted.",
        )

    # =====================================================
    # APPROVAL NOTIFICATIONS
    # =====================================================

    def test_notify_edit_request_submitted(self):
        notification = notify_edit_request_submitted(
            recipient=self.user,
            edit_request=self.edit_request,
        )

        self.assertEqual(
            notification.notification_type,
            "approval",
        )

        self.assertEqual(
            notification.title,
            "Edit Request Submitted",
        )

        self.assertEqual(
            notification.message,
            (
                f"Your request to edit Time Entry "
                f"#{self.time_entry.id} has been submitted."
            ),
        )

    def test_notify_edit_request_approved(self):
        notification = notify_edit_request_approved(
            recipient=self.user,
            edit_request=self.edit_request,
        )

        self.assertEqual(
            notification.notification_type,
            "approval",
        )

        self.assertEqual(
            notification.title,
            "Edit Request Approved",
        )

        self.assertEqual(
            notification.message,
            (
                f"Your request for Time Entry "
                f"#{self.time_entry.id} has been approved."
            ),
        )

    def test_notify_edit_request_rejected(self):
        notification = notify_edit_request_rejected(
            recipient=self.user,
            edit_request=self.edit_request,
        )

        self.assertEqual(
            notification.notification_type,
            "approval",
        )

        self.assertEqual(
            notification.title,
            "Edit Request Rejected",
        )

        self.assertEqual(
            notification.message,
            (
                f"Your request for Time Entry "
                f"#{self.time_entry.id} has been rejected."
            ),
        )

    # =====================================================
    # QUERY SERVICES
    # =====================================================

    def test_get_notifications_returns_only_users_notifications(
        self,
    ):
        create_notification(
            recipient=self.user,
            notification_type="system",
            title="User Notification",
            message="For user.",
        )

        create_notification(
            recipient=self.other_user,
            notification_type="system",
            title="Other Notification",
            message="For other user.",
        )

        notifications = get_notifications(
            self.user
        )

        self.assertEqual(
            notifications.count(),
            1,
        )

        self.assertEqual(
            notifications.first().recipient,
            self.user,
        )

    def test_get_unread_notifications(self):
        unread = create_notification(
            recipient=self.user,
            notification_type="system",
            title="Unread",
            message="Unread notification.",
        )

        read = create_notification(
            recipient=self.user,
            notification_type="system",
            title="Read",
            message="Read notification.",
        )

        read.is_read = True
        read.save(
            update_fields=["is_read"]
        )

        notifications = get_unread_notifications(
            self.user
        )

        self.assertEqual(
            notifications.count(),
            1,
        )

        self.assertEqual(
            notifications.first().pk,
            unread.pk,
        )

    # =====================================================
    # MARK AS READ
    # =====================================================

    def test_mark_notification_as_read(self):
        notification = create_notification(
            recipient=self.user,
            notification_type="system",
            title="Unread",
            message="Unread notification.",
        )

        self.assertFalse(
            notification.is_read
        )

        result = mark_notification_as_read(
            notification
        )

        self.assertTrue(
            result.is_read
        )

        notification.refresh_from_db()

        self.assertTrue(
            notification.is_read
        )

    def test_mark_all_notifications_as_read(self):
        first = create_notification(
            recipient=self.user,
            notification_type="system",
            title="First",
            message="First notification.",
        )

        second = create_notification(
            recipient=self.user,
            notification_type="system",
            title="Second",
            message="Second notification.",
        )

        other = create_notification(
            recipient=self.other_user,
            notification_type="system",
            title="Other",
            message="Other notification.",
        )

        count = mark_all_notifications_as_read(
            self.user
        )

        self.assertEqual(
            count,
            2,
        )

        first.refresh_from_db()
        second.refresh_from_db()
        other.refresh_from_db()

        self.assertTrue(
            first.is_read
        )

        self.assertTrue(
            second.is_read
        )

        self.assertFalse(
            other.is_read
        )

    def test_mark_all_notifications_as_read_returns_zero_when_none_unread(
        self,
    ):
        notification = create_notification(
            recipient=self.user,
            notification_type="system",
            title="Already Read",
            message="Already read notification.",
        )

        notification.is_read = True
        notification.save(
            update_fields=["is_read"]
        )

        count = mark_all_notifications_as_read(
            self.user
        )

        self.assertEqual(
            count,
            0,
        )
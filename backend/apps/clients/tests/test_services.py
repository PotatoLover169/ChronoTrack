from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.clients.models import Client
from apps.clients.services import (
    get_accessible_projects,
    get_client_dashboard,
    is_manager_or_admin,
)
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.tracker.models import (
    TimeEntry,
    TimeEntryStatus,
)


User = get_user_model()


class ClientServicesTestCase(TestCase):

    def setUp(self):
        self.employee = User.objects.create_user(
            username="employee",
            email="employee@example.com",
            password="TestPassword123!",
        )

        self.other_employee = User.objects.create_user(
            username="other_employee",
            email="other@example.com",
            password="TestPassword123!",
        )

        self.manager = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="TestPassword123!",
        )

        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="TestPassword123!",
        )

        manager_group, _ = Group.objects.get_or_create(
            name="Manager"
        )

        admin_group, _ = Group.objects.get_or_create(
            name="Admin"
        )

        self.manager.groups.add(
            manager_group
        )

        self.admin.groups.add(
            admin_group
        )

        self.client = Client.objects.create(
            owner=self.employee,
            name="Acme Client",
            company="Acme Corporation",
            email="client@acme.com",
            phone="09171234567",
            notes="Primary client",
        )

        self.other_client = Client.objects.create(
            owner=self.other_employee,
            name="Other Client",
            company="Other Corporation",
        )

        self.employee_project = Project.objects.create(
            owner=self.employee,
            client=self.client,
            name="Employee Project",
            status="in_progress",
            hourly_rate=Decimal("100.00"),
        )

        self.member_project = Project.objects.create(
            owner=self.other_employee,
            client=self.client,
            name="Member Project",
            status="completed",
            hourly_rate=Decimal("150.00"),
        )

        self.member_project.members.add(
            self.employee
        )

        self.inaccessible_project = Project.objects.create(
            owner=self.other_employee,
            client=self.other_client,
            name="Inaccessible Project",
            status="in_progress",
            hourly_rate=Decimal("200.00"),
        )

        self.completed_entry = self.create_time_entry(
            project=self.employee_project,
            hours=2,
            billable=True,
        )

        self.non_billable_entry = self.create_time_entry(
            project=self.employee_project,
            hours=1,
            billable=False,
        )

        self.member_entry = self.create_time_entry(
            project=self.member_project,
            hours=3,
            billable=True,
        )

        self.running_entry = TimeEntry.objects.create(
            owner=self.employee,
            project=self.employee_project,
            description="Running timer",
            start_time=timezone.now(),
            billable=True,
            status=TimeEntryStatus.RUNNING,
        )

    def create_time_entry(
        self,
        *,
        project,
        hours,
        billable=True,
        owner=None,
    ):
        owner = owner or project.owner

        start_time = timezone.now() - timedelta(
            hours=hours
        )

        end_time = timezone.now()

        return TimeEntry.objects.create(
            owner=owner,
            project=project,
            description="Client dashboard test entry",
            start_time=start_time,
            end_time=end_time,
            billable=billable,
            status=TimeEntryStatus.COMPLETED,
        )

    # ---------------------------------------------------------
    # ROLE HELPERS
    # ---------------------------------------------------------

    def test_employee_is_not_manager_or_admin(self):
        self.assertFalse(
            is_manager_or_admin(
                self.employee
            )
        )

    def test_manager_is_manager_or_admin(self):
        self.assertTrue(
            is_manager_or_admin(
                self.manager
            )
        )

    def test_admin_is_manager_or_admin(self):
        self.assertTrue(
            is_manager_or_admin(
                self.admin
            )
        )

    def test_superuser_is_manager_or_admin(self):
        self.admin.is_superuser = True
        self.admin.save(
            update_fields=["is_superuser"]
        )

        self.assertTrue(
            is_manager_or_admin(
                self.admin
            )
        )

    # ---------------------------------------------------------
    # ACCESSIBLE PROJECTS
    # ---------------------------------------------------------

    def test_employee_can_access_owned_client_projects(self):
        projects = get_accessible_projects(
            user=self.employee,
            client=self.client,
        )

        self.assertIn(
            self.employee_project,
            projects,
        )

    def test_employee_can_access_projects_where_member(self):
        projects = get_accessible_projects(
            user=self.employee,
            client=self.client,
        )

        self.assertIn(
            self.member_project,
            projects,
        )

    def test_employee_cannot_access_unrelated_client_projects(self):
        projects = get_accessible_projects(
            user=self.employee,
            client=self.other_client,
        )

        self.assertNotIn(
            self.inaccessible_project,
            projects,
        )

        self.assertEqual(
            projects.count(),
            0,
        )

    def test_manager_can_access_all_client_projects(self):
        projects = get_accessible_projects(
            user=self.manager,
            client=self.client,
        )

        self.assertEqual(
            projects.count(),
            2,
        )

        self.assertIn(
            self.employee_project,
            projects,
        )

        self.assertIn(
            self.member_project,
            projects,
        )

    def test_admin_can_access_all_client_projects(self):
        projects = get_accessible_projects(
            user=self.admin,
            client=self.client,
        )

        self.assertEqual(
            projects.count(),
            2,
        )

    # ---------------------------------------------------------
    # CLIENT DASHBOARD ACCESS
    # ---------------------------------------------------------

    def test_employee_can_view_dashboard_for_owned_client(self):
        result = get_client_dashboard(
            user=self.employee,
            client_id=self.client.id,
        )

        self.assertEqual(
            result["client"],
            self.client,
        )

    def test_employee_can_view_dashboard_for_client_with_membership(
        self,
    ):
        result = get_client_dashboard(
            user=self.employee,
            client_id=self.client.id,
        )

        self.assertEqual(
            result["client"].id,
            self.client.id,
        )

    def test_employee_cannot_view_unrelated_client_dashboard(self):
        with self.assertRaises(
            Client.DoesNotExist
        ):
            get_client_dashboard(
                user=self.employee,
                client_id=self.other_client.id,
            )

    def test_manager_can_view_any_client_dashboard(self):
        result = get_client_dashboard(
            user=self.manager,
            client_id=self.client.id,
        )

        self.assertEqual(
            result["client"].id,
            self.client.id,
        )

    def test_admin_can_view_any_client_dashboard(self):
        result = get_client_dashboard(
            user=self.admin,
            client_id=self.other_client.id,
        )

        self.assertEqual(
            result["client"].id,
            self.other_client.id,
        )

    def test_missing_client_raises_does_not_exist(self):
        with self.assertRaises(
            Client.DoesNotExist
        ):
            get_client_dashboard(
                user=self.employee,
                client_id=999999,
            )

    # ---------------------------------------------------------
    # DASHBOARD COUNTS
    # ---------------------------------------------------------

    def test_dashboard_project_counts(self):
        result = get_client_dashboard(
            user=self.employee,
            client_id=self.client.id,
        )

        self.assertEqual(
            result["total_projects"],
            2,
        )

        self.assertEqual(
            result["active_projects"],
            1,
        )

        self.assertEqual(
            result["completed_projects"],
            1,
        )

    def test_dashboard_task_counts(self):
        Task.objects.create(
            owner=self.employee,
            project=self.employee_project,
            title="Completed Client Task",
            status="completed",
            completed=True,
        )

        Task.objects.create(
            owner=self.employee,
            project=self.employee_project,
            title="Open Client Task",
            status="todo",
            completed=False,
        )

        result = get_client_dashboard(
            user=self.employee,
            client_id=self.client.id,
        )

        self.assertEqual(
            result["total_tasks"],
            2,
        )

        self.assertEqual(
            result["completed_tasks"],
            1,
        )

    def test_dashboard_entry_count(self):
        result = get_client_dashboard(
            user=self.employee,
            client_id=self.client.id,
        )

        self.assertEqual(
            result["total_entries"],
            3,
        )

    # ---------------------------------------------------------
    # HOURS / BILLABLE / EARNINGS
    # ---------------------------------------------------------

    def test_dashboard_total_hours(self):
        result = get_client_dashboard(
            user=self.employee,
            client_id=self.client.id,
        )

        self.assertEqual(
            result["total_hours"],
            Decimal("6.00"),
        )

    def test_dashboard_billable_hours(self):
        result = get_client_dashboard(
            user=self.employee,
            client_id=self.client.id,
        )

        self.assertEqual(
            result["billable_hours"],
            Decimal("5.00"),
        )

    def test_dashboard_non_billable_hours(self):
        result = get_client_dashboard(
            user=self.employee,
            client_id=self.client.id,
        )

        self.assertEqual(
            result["non_billable_hours"],
            Decimal("1.00"),
        )

    def test_dashboard_total_earnings(self):
        result = get_client_dashboard(
            user=self.employee,
            client_id=self.client.id,
        )

        expected = Decimal("650.00")

        self.assertEqual(
            result["total_earnings"],
            expected,
        )

    # ---------------------------------------------------------
    # COMPLETED ENTRY FILTER
    # ---------------------------------------------------------

    def test_dashboard_excludes_running_entries(self):
        result = get_client_dashboard(
            user=self.employee,
            client_id=self.client.id,
        )

        self.assertEqual(
            result["total_entries"],
            3,
        )

        self.assertNotEqual(
            result["total_entries"],
            4,
        )

    def test_dashboard_ignores_entries_without_duration(self):
        TimeEntry.objects.create(
            owner=self.employee,
            project=self.employee_project,
            description="No duration entry",
            start_time=timezone.now(),
            billable=True,
            status=TimeEntryStatus.COMPLETED,
        )

        result = get_client_dashboard(
            user=self.employee,
            client_id=self.client.id,
        )

        self.assertEqual(
            result["total_entries"],
            4,
        )

        self.assertEqual(
            result["total_hours"],
            Decimal("6.00"),
        )
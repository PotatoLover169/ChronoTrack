from rest_framework import serializers

from apps.projects.api.serializers import (
    ProjectSummarySerializer,
)
from apps.tasks.api.serializers import (
    TaskSummarySerializer,
)

from apps.tracker.models import TimeEntry

class DashboardCurrentTimerSerializer(
    serializers.Serializer,
):
    id = serializers.IntegerField()

    project = ProjectSummarySerializer()

    task = TaskSummarySerializer(
        allow_null=True,
    )

    description = serializers.CharField()

    start_time = serializers.DateTimeField()

    elapsed_seconds = serializers.IntegerField()

class DashboardTodaySerializer(
    serializers.Serializer,
):
    hours = serializers.FloatField()

    billable_hours = serializers.FloatField()

    earnings = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    entries = serializers.IntegerField()

    completed_tasks = serializers.IntegerField()

class DashboardWeekSerializer(
    serializers.Serializer,
):
    hours = serializers.FloatField()

    billable_hours = serializers.FloatField()

    earnings = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    entries = serializers.IntegerField()

    completed_tasks = serializers.IntegerField()

class DashboardMonthSerializer(
    serializers.Serializer,
):
    hours = serializers.FloatField()

    billable_hours = serializers.FloatField()

    earnings = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    entries = serializers.IntegerField()

    completed_tasks = serializers.IntegerField()

class DashboardSummarySerializer(serializers.Serializer):
    running_timer = serializers.BooleanField()

    current_timer = DashboardCurrentTimerSerializer(
        allow_null=True,
    )

    today = DashboardTodaySerializer()

    week = DashboardWeekSerializer()

    month = DashboardMonthSerializer()

    today_hours = serializers.FloatField()

    this_week_hours = serializers.FloatField()

    this_month_hours = serializers.FloatField()

    active_projects = serializers.IntegerField()

    completed_projects = serializers.IntegerField()

    total_clients = serializers.IntegerField()

    billable_hours = serializers.FloatField()

    estimated_earnings = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    pending_approvals = serializers.IntegerField()


class DashboardRecentEntrySerializer(serializers.ModelSerializer):
    project = ProjectSummarySerializer(
        read_only=True,
    )

    task = TaskSummarySerializer(
        read_only=True,
    )

    class Meta:
        model = TimeEntry

        fields = (
            "id",
            "project",
            "task",
            "description",
            "start_time",
            "end_time",
            "duration",
            "billable",
            "status",
        )


class DashboardTopProjectSerializer(
    serializers.Serializer,
):
    project = ProjectSummarySerializer()

    hours = serializers.FloatField()

    earnings = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

class DashboardHoursPerDaySerializer(
    serializers.Serializer,
):
    date = serializers.DateField()

    hours = serializers.FloatField()

class DashboardBillableBreakdownSerializer(
    serializers.Serializer,
):
    billable_hours = serializers.FloatField()

    non_billable_hours = serializers.FloatField()

class DashboardProjectStatusBreakdownSerializer(
    serializers.Serializer,
):
    planning = serializers.IntegerField()

    in_progress = serializers.IntegerField()

    on_hold = serializers.IntegerField()

    completed = serializers.IntegerField()

    cancelled = serializers.IntegerField()

class DashboardChartItemSerializer(
    serializers.Serializer,
):
    label = serializers.CharField()

    value = serializers.FloatField()

class DashboardChartsSerializer(
    serializers.Serializer,
):
    hours_per_day = DashboardChartItemSerializer(
        many=True,
    )

    billable = DashboardChartItemSerializer(
        many=True,
    )

    project_status = DashboardChartItemSerializer(
        many=True,
    )

class DashboardSerializer(serializers.Serializer):
    summary = DashboardSummarySerializer()

    recent_entries = DashboardRecentEntrySerializer(
        many=True,
    )

    top_projects = DashboardTopProjectSerializer(
        many=True,
    )

    hours_per_day = DashboardHoursPerDaySerializer(
        many=True,
    )

    billable_breakdown = (
        DashboardBillableBreakdownSerializer()
    )

    project_status_breakdown = (
        DashboardProjectStatusBreakdownSerializer()
    )

    charts = DashboardChartsSerializer()
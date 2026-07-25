from rest_framework import serializers

from apps.projects.api.serializers import ProjectSummarySerializer
from apps.tasks.api.serializers import TaskSummarySerializer

from apps.tracker.models import TimeEntry


class DashboardSummarySerializer(serializers.Serializer):
    running_timer = serializers.BooleanField()

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


class DashboardSerializer(serializers.Serializer):
    summary = DashboardSummarySerializer()

    recent_entries = DashboardRecentEntrySerializer(
        many=True,
    )
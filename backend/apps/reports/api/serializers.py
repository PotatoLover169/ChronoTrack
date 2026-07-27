from rest_framework import serializers

from apps.tracker.models import TimeEntry


class ReportSummarySerializer(serializers.Serializer):
    total_entries = serializers.IntegerField()

    completed_entries = serializers.IntegerField()

    billable_entries = serializers.IntegerField()

    non_billable_entries = serializers.IntegerField()

    total_duration_hours = serializers.FloatField()

    billable_hours = serializers.FloatField()

    estimated_earnings = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )


class TimesheetReportSerializer(
    serializers.ModelSerializer,
):
    project = serializers.SerializerMethodField()

    task = serializers.SerializerMethodField()

    date = serializers.SerializerMethodField()

    earnings = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = TimeEntry

        fields = (
            "id",
            "project",
            "task",
            "date",
            "start_time",
            "end_time",
            "duration",
            "billable",
            "hourly_rate",
            "earnings",
        )

    def get_project(self, obj):
        return obj.project.name

    def get_task(self, obj):
        if obj.task:
            return obj.task.title

        return None

    def get_date(self, obj):
        return obj.start_time.date()    
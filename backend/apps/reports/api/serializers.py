from rest_framework import serializers

from apps.tracker.models import TimeEntry


class ReportSummarySerializer(
    serializers.Serializer,
):
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

    def get_project(
        self,
        obj,
    ):
        return obj.project.name

    def get_task(
        self,
        obj,
    ):
        if obj.task:
            return obj.task.title

        return None

    def get_date(
        self,
        obj,
    ):
        return obj.start_time.date()


# ==========================================================
# Daily Report Serializers
# ==========================================================


class DailyReportEntrySerializer(
    serializers.ModelSerializer,
):
    """
    Individual time entry shown inside
    the Daily Report.
    """

    project = serializers.CharField(
        source="project.name",
        read_only=True,
    )

    task = serializers.SerializerMethodField()

    duration_hours = serializers.SerializerMethodField()

    earnings = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
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
            "duration_hours",
            "billable",
            "earnings",
        )

    def get_task(
        self,
        obj,
    ):
        if obj.task:
            return obj.task.title

        return None

    def get_duration_hours(
        self,
        obj,
    ):
        if not obj.duration:
            return 0

        return round(
            obj.duration.total_seconds() / 3600,
            2,
        )


class DailyReportSerializer(
    serializers.Serializer,
):
    """
    Serializer for the Daily Report endpoint.
    """

    date = serializers.DateField()

    total_entries = serializers.IntegerField()

    total_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    billable_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    non_billable_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    total_earnings = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    entries = DailyReportEntrySerializer(
        many=True,
    )


# ==========================================================
# Weekly Report Serializer
# ==========================================================


class WeeklyReportSerializer(
    serializers.Serializer,
):
    """
    Serializer for the Weekly Report endpoint.
    """

    week_start = serializers.DateField()

    week_end = serializers.DateField()

    total_entries = serializers.IntegerField()

    total_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    billable_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    non_billable_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    total_earnings = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    entries = DailyReportEntrySerializer(
        many=True,
    )


# ==========================================================
# Monthly Report Serializer
# ==========================================================


class MonthlyReportSerializer(
    serializers.Serializer,
):
    """
    Serializer for the Monthly Report endpoint.
    """

    month = serializers.CharField()

    year = serializers.IntegerField()

    total_entries = serializers.IntegerField()

    total_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    billable_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    non_billable_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    total_earnings = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    entries = DailyReportEntrySerializer(
        many=True,
    )

# ==========================================================
# Project Report Serializers
# ==========================================================


class ProjectReportSerializer(
    serializers.Serializer,
):
    """
    Serializer for the Project Report endpoint.
    """

    project = serializers.SerializerMethodField()

    total_entries = serializers.IntegerField()

    total_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    billable_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    non_billable_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    total_earnings = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    entries = DailyReportEntrySerializer(
        many=True,
    )

    def get_project(
        self,
        obj,
    ):
        project = obj["project"]

        return {
            "id": project.id,
            "name": project.name,
            "client": project.client.name,
            "status": project.status,
            "hourly_rate": project.hourly_rate,
        }

# ==========================================================
# Client Report Serializer
# ==========================================================


class ClientReportSerializer(
    serializers.Serializer,
):
    """
    Serializer for the Client Report endpoint.
    """

    client = serializers.SerializerMethodField()

    total_entries = serializers.IntegerField()

    total_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    billable_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    non_billable_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    total_earnings = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    entries = DailyReportEntrySerializer(
        many=True,
    )

    def get_client(
        self,
        obj,
    ):
        client = obj["client"]

        return {
            "id": client.id,
            "name": client.name,
        }

# ==========================================================
# Dashboard Analytics Serializers
# ==========================================================


class DashboardProjectSerializer(
    serializers.Serializer,
):
    id = serializers.IntegerField(
        source="project__id",
    )

    name = serializers.CharField(
        source="project__name",
    )


class DashboardClientSerializer(
    serializers.Serializer,
):
    id = serializers.IntegerField(
        source="project__client__id",
    )

    name = serializers.CharField(
        source="project__client__name",
    )


class DashboardAnalyticsSerializer(
    serializers.Serializer,
):
    today_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    week_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    month_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    completed_entries = serializers.IntegerField()

    billable_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    non_billable_hours = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    estimated_earnings = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    active_projects = serializers.IntegerField()

    completed_projects = serializers.IntegerField()

    top_project = DashboardProjectSerializer(
        allow_null=True,
    )

    top_client = DashboardClientSerializer(
        allow_null=True,
    )
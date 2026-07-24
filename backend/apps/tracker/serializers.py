from django.utils import timezone
from rest_framework import serializers

from apps.projects.api.serializers import ProjectSummarySerializer
from apps.projects.models import Project
from apps.tasks.api.serializers import TaskSummarySerializer
from apps.tasks.models import Task

from .models import TimeEntry


class StartTimerSerializer(serializers.Serializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
    )

    task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        required=False,
        allow_null=True,
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def validate(self, attrs):
        """
        Ensure the selected task belongs to the selected project.
        """
        project = attrs["project"]
        task = attrs.get("task")

        if task and task.project != project:
            raise serializers.ValidationError(
                {
                    "task": (
                        "The selected task does not belong "
                        "to the selected project."
                    )
                }
            )

        return attrs


class CurrentTimerSerializer(serializers.ModelSerializer):
    project = ProjectSummarySerializer(
        read_only=True,
    )

    task = TaskSummarySerializer(
        read_only=True,
    )

    elapsed_seconds = serializers.SerializerMethodField()

    elapsed_time = serializers.SerializerMethodField()

    class Meta:
        model = TimeEntry
        fields = (
            "id",
            "project",
            "task",
            "description",
            "start_time",
            "status",
            "elapsed_seconds",
            "elapsed_time",
        )

    def get_elapsed_seconds(self, obj):
        """
        Returns the number of elapsed seconds since the timer started.
        """

        if not obj.start_time:
            return 0

        end_time = obj.end_time or timezone.now()

        return int(
            (end_time - obj.start_time).total_seconds()
        )

    def get_elapsed_time(self, obj):
        """
        Returns the elapsed time formatted as HH:MM:SS.
        """

        seconds = self.get_elapsed_seconds(obj)

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return (
            f"{hours:02}:{minutes:02}:{seconds:02}"
        )

class TimeEntrySerializer(serializers.ModelSerializer):
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

class TimeEntrySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeEntry

        fields = (
            "id",
            "status",
            "start_time",
            "end_time",
            "duration",
        )
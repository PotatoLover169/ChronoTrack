from rest_framework import serializers

from apps.projects.api.serializers import ProjectSummarySerializer
from apps.projects.models import Project
from apps.tasks.models import Task


class TaskSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "status",
            "priority",
        )


class TaskSerializer(serializers.ModelSerializer):
    project = ProjectSummarySerializer(read_only=True)

    project_id = serializers.PrimaryKeyRelatedField(
        source="project",
        queryset=Project.objects.none(),
        write_only=True,
    )

    class Meta:
        model = Task
        fields = (
            "id",
            "owner",
            "project",
            "project_id",
            "title",
            "description",
            "priority",
            "status",
            "estimated_hours",
            "actual_hours",
            "due_date",
            "completed",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "owner",
            "project",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        status = attrs.get(
            "status",
            getattr(self.instance, "status", "todo"),
        )

        attrs["completed"] = status == "completed"

        return attrs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            self.fields["project_id"].queryset = Project.objects.filter(
                owner=request.user
            )
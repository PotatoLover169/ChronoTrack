from rest_framework import serializers

from apps.projects.models import Project
from apps.tasks.models import Task


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
                    "task": "The selected task does not belong to the selected project."
                }
            )

        return attrs
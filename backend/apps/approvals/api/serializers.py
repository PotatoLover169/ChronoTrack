from rest_framework import serializers

from apps.approvals.models import TimeEntryEditRequest
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.tracker.models import TimeEntry


class TimeEntryEditRequestSerializer(serializers.ModelSerializer):
    time_entry = serializers.PrimaryKeyRelatedField(
        queryset=TimeEntry.objects.none(),
    )

    requested_project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.none(),
        required=False,
        allow_null=True,
    )

    requested_task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.none(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = TimeEntryEditRequest

        fields = (
            "id",
            "time_entry",
            "requested_project",
            "requested_task",
            "requested_start_time",
            "requested_end_time",
            "requested_description",
            "requested_billable",
            "reason",
            "proof_screenshot",
        )

        read_only_fields = (
            "id",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            self.fields["time_entry"].queryset = (
                TimeEntry.objects.filter(
                    owner=request.user,
                )
            )

            self.fields["requested_project"].queryset = (
                Project.objects.filter(
                    owner=request.user,
                )
            )

            self.fields["requested_task"].queryset = (
                Task.objects.filter(
                    owner=request.user,
                )
            )


class TimeEntryEditRequestDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeEntryEditRequest

        fields = (
            "id",
            "time_entry",
            "requested_by",
            "reviewed_by",
            "requested_project",
            "requested_task",
            "requested_start_time",
            "requested_end_time",
            "requested_description",
            "requested_billable",
            "reason",
            "proof_screenshot",
            "status",
            "manager_comment",
            "requested_at",
            "reviewed_at",
        )

        read_only_fields = fields


class ManagerCommentSerializer(serializers.Serializer):
    """
    Serializer used by managers when approving or rejecting
    a Time Entry Edit Request.
    """

    manager_comment = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )
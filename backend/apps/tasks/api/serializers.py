from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.projects.api.serializers import ProjectSummarySerializer
from apps.projects.models import Project
from apps.tasks.models import Task


User = get_user_model()


class TaskSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "status",
            "priority",
        )


class AssignedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
        )


class TaskSerializer(serializers.ModelSerializer):
    project = ProjectSummarySerializer(read_only=True)

    project_id = serializers.PrimaryKeyRelatedField(
        source="project",
        queryset=Project.objects.none(),
        write_only=True,
    )

    assigned_to = AssignedUserSerializer(read_only=True)

    assigned_to_id = serializers.PrimaryKeyRelatedField(
        source="assigned_to",
        queryset=User.objects.none(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Task

        fields = (
            "id",
            "owner",
            "project",
            "project_id",
            "assigned_to",
            "assigned_to_id",
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
            "assigned_to",
            "actual_hours",
            "completed",
            "created_at",
            "updated_at",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return

        user = request.user

        is_manager_or_admin = (
            user.is_superuser
            or user.groups.filter(
                name__in=["Manager", "Admin"]
            ).exists()
        )

        # -----------------------------------------
        # PROJECT ACCESS
        # -----------------------------------------

        if is_manager_or_admin:
            self.fields["project_id"].queryset = Project.objects.all()
        else:
            self.fields["project_id"].queryset = Project.objects.filter(
                members=user
            )

        # -----------------------------------------
        # TASK ASSIGNMENT
        # -----------------------------------------

        if is_manager_or_admin:
            self.fields["assigned_to_id"].queryset = User.objects.filter(
                is_active=True
            )
        else:
            # Employees cannot assign or reassign tasks.
            self.fields["assigned_to_id"].queryset = User.objects.none()

    def validate(self, attrs):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            user = request.user

            is_manager_or_admin = (
                user.is_superuser
                or user.groups.filter(
                    name__in=["Manager", "Admin"]
                ).exists()
            )

            if not is_manager_or_admin:

                # -----------------------------------------
                # EMPLOYEE UPDATE RESTRICTIONS
                # -----------------------------------------

                # Employees can only update task status.
                incoming_fields = set(self.initial_data.keys())

                allowed_employee_fields = {"status"}

                unauthorized_fields = (
                    incoming_fields - allowed_employee_fields
                )

                if unauthorized_fields:
                    raise serializers.ValidationError(
                        {
                            "detail": (
                                "Employees can only update task status."
                            )
                        }
                    )

        # -----------------------------------------
        # COMPLETED STATUS
        # -----------------------------------------

        status = attrs.get(
            "status",
            getattr(self.instance, "status", "todo")
        )

        attrs["completed"] = status == "completed"

        return attrs
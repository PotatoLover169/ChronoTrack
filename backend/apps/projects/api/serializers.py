from rest_framework import serializers

from apps.clients.models import Client
from apps.projects.models import Project


class ClientSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ("id", "name")


class ProjectSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "name", "status", "hourly_rate")


class ProjectSerializer(serializers.ModelSerializer):
    client = ClientSummarySerializer(read_only=True)

    client_id = serializers.PrimaryKeyRelatedField(
        source="client",
        queryset=Client.objects.none(),
        write_only=True,
    )

    class Meta:
        model = Project
        fields = (
            "id",
            "owner",
            "client",
            "client_id",
            "name",
            "description",
            "status",
            "start_date",
            "end_date",
            "hourly_rate",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "owner",
            "client",
            "created_at",
            "updated_at",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return

        user = request.user

        # Managers and Admins can select any client
        if (
            user.is_superuser
            or user.groups.filter(
                name__in=["Admin", "Manager"]
            ).exists()
        ):
            self.fields["client_id"].queryset = Client.objects.all()

        # Employees can only select clients they own.
        # Employees should normally not create projects,
        # so this is mainly a safety fallback.
        else:
            self.fields["client_id"].queryset = Client.objects.filter(
                owner=user
            )
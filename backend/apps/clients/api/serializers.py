from rest_framework import serializers

from apps.clients.models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"
        read_only_fields = (
            "id",
            "owner",
            "created_at",
            "updated_at",
        )

class ClientDashboardSerializer(
    serializers.Serializer,
):
    """
    Dashboard statistics for a client.
    """

    client = serializers.SerializerMethodField()

    total_projects = serializers.IntegerField()

    active_projects = serializers.IntegerField()

    completed_projects = serializers.IntegerField()

    total_tasks = serializers.IntegerField()

    completed_tasks = serializers.IntegerField()

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

    def get_client(
        self,
        obj,
    ):
        client = obj["client"]

        return {
            "id": client.id,
            "name": client.name,
        }
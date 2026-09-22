from rest_framework import serializers

from apps.clients.models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "id",
            "name",
            "company",
            "email",
            "phone",
            "notes",
            "created_at",
            "updated_at",
            "owner",
        ]
        read_only_fields = [
            "id",
            "owner",
            "created_at",
            "updated_at",
        ]


class ClientDashboardSerializer(
    serializers.Serializer,
):
    client = serializers.SerializerMethodField()

    total_projects = serializers.IntegerField()
    active_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()

    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()

    total_entries = serializers.IntegerField()

    total_hours = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    billable_hours = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    non_billable_hours = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    total_earnings = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
    )

    def get_client(self, obj):
        client = obj["client"]

        return {
            "id": client.id,
            "name": client.name,
        }
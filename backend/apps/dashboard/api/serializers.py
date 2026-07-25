from rest_framework import serializers


class DashboardSerializer(serializers.Serializer):
    running_timer = serializers.BooleanField()

    today_hours = serializers.FloatField()

    this_week_hours = serializers.FloatField()

    this_month_hours = serializers.FloatField()

    active_projects = serializers.IntegerField()

    completed_projects = serializers.IntegerField()

    total_clients = serializers.IntegerField()

    billable_hours = serializers.FloatField()

    estimated_earnings = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    pending_approvals = serializers.IntegerField()
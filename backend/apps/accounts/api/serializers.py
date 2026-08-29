from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
    )

    class Meta:
        model = User

        fields = (
            "id",
            "username",
            "email",
            "password",
        )

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = (
            "id",
            "username",
            "email",
            "role",
        )

    def get_role(self, obj):
        if obj.is_superuser:
            return "Admin"

        group = obj.groups.first()

        if group:
            return group.name

        return "Employee"


class UserSummarySerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "role",
        )

    def get_role(self, obj):
        if obj.is_superuser:
            return "Admin"

        group = obj.groups.first()

        if group:
            return group.name

        return "Employee"


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = (
            "first_name",
            "last_name",
            "email",
        )
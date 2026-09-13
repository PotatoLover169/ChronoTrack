from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .permissions import (
    IsAdminUserRole,
    IsManagerOrAdminRole,
)

from .serializers import (
    RegisterSerializer,
    UpdateProfileSerializer,
    UserSerializer,
    AdminCreateUserSerializer,
    AdminUserSerializer,
    AssignableUserSerializer,
)


User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UpdateProfileAPIView(generics.UpdateAPIView):
    """
    Update the authenticated user's profile.
    """

    serializer_class = UpdateProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class AdminCreateUserAPIView(generics.CreateAPIView):
    """
    Allows administrators to create Manager
    and Employee accounts.
    """

    serializer_class = AdminCreateUserSerializer
    permission_classes = [IsAdminUserRole]


class AdminUserListAPIView(generics.ListAPIView):
    """
    Allows administrators to view all users.
    """

    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        return User.objects.all().order_by("-date_joined")

class AssignableUserListAPIView(generics.ListAPIView):
    """
    Return active Employee accounts that can be assigned
    to tasks by Managers and Administrators.
    """

    serializer_class = AssignableUserSerializer
    permission_classes = [IsManagerOrAdminRole]

    def get_queryset(self):
        return (
            User.objects
            .filter(
                is_active=True,
                groups__name="Employee",
            )
            .distinct()
            .order_by(
                "first_name",
                "last_name",
                "username",
            )
        )
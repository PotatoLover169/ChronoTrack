from django.db import models

from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
)
from rest_framework.response import Response

from apps.clients.models import Client
from apps.clients.services import get_client_dashboard

from .serializers import (
    ClientSerializer,
    ClientDashboardSerializer,
)


def is_manager_or_admin(user):
    return (
        user.is_superuser
        or user.groups.filter(
            name__in=["Admin", "Manager"]
        ).exists()
    )


class IsManagerOrAdminForMutation(
    BasePermission,
):
    """
    Allow authenticated users to read clients.

    Only Managers and Admins can create,
    update, or delete clients.
    """

    def has_permission(
        self,
        request,
        view,
    ):
        if request.method in (
            "GET",
            "HEAD",
            "OPTIONS",
        ):
            return True

        return is_manager_or_admin(
            request.user,
        )


class ClientListCreateAPIView(
    generics.ListCreateAPIView,
):
    serializer_class = ClientSerializer

    permission_classes = [
        IsAuthenticated,
        IsManagerOrAdminForMutation,
    ]

    def get_queryset(self):
        user = self.request.user

        # Managers and Admins can view all clients.
        if is_manager_or_admin(user):
            return Client.objects.all()

        # Employees can view clients connected
        # to projects they own or are assigned to.
        return Client.objects.filter(
            models.Q(projects__owner=user)
            | models.Q(projects__members=user)
            | models.Q(owner=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user,
        )


class ClientRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView,
):
    serializer_class = ClientSerializer

    permission_classes = [
        IsAuthenticated,
        IsManagerOrAdminForMutation,
    ]

    def get_queryset(self):
        user = self.request.user

        # Managers and Admins can access all clients.
        if is_manager_or_admin(user):
            return Client.objects.all()

        # Employees can only access clients connected
        # to projects they own or are assigned to.
        return Client.objects.filter(
            models.Q(projects__owner=user)
            | models.Q(projects__members=user)
            | models.Q(owner=user)
        ).distinct()


class ClientDashboardAPIView(
    generics.GenericAPIView,
):
    """
    Return dashboard statistics for a client.
    """

    serializer_class = ClientDashboardSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
        pk,
    ):
        try:
            data = get_client_dashboard(
                user=request.user,
                client_id=pk,
            )
        except Client.DoesNotExist:
            raise NotFound(
                "Client not found or you do not have access to this client."
            )

        serializer = self.get_serializer(
            data,
        )

        return Response(
            serializer.data,
        )
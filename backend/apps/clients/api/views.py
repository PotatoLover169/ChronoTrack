from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
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


class ClientListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if is_manager_or_admin(user):
            return Client.objects.all()

        return Client.objects.filter(
            owner=user
        )

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user
        )


class ClientRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if is_manager_or_admin(user):
            return Client.objects.all()

        return Client.objects.filter(
            owner=user
        )


class ClientDashboardAPIView(
    generics.GenericAPIView,
):
    """
    Return dashboard statistics
    for a specific client.
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
        data = get_client_dashboard(
            user=request.user,
            client_id=pk,
        )

        serializer = self.get_serializer(
            data,
        )

        return Response(
            serializer.data,
        )
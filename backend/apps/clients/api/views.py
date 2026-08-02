from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.clients.services import (
    get_client_dashboard,
)

from .serializers import (
    ClientSerializer,
    ClientDashboardSerializer,
)

from .serializers import ClientSerializer


class ClientListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ClientRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

class ClientDashboardAPIView(
    generics.GenericAPIView,
):
    """
    Return dashboard statistics
    for a specific client.
    """

    serializer_class = (
        ClientDashboardSerializer
    )

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
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.dashboard.services import get_dashboard_data

from .serializers import DashboardSerializer


class HealthCheckAPIView(APIView):
    """
    Health check endpoint.
    """

    permission_classes = []

    def get(self, request):
        return Response(
            {
                "status": "success",
                "message": "ChronoTrack API is running",
                "version": "1.0.0",
            }
        )


class DashboardAPIView(generics.GenericAPIView):
    """
    Return dashboard statistics for the authenticated user.
    """

    serializer_class = DashboardSerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get(self, request):
        data = get_dashboard_data(
            request.user,
        )

        serializer = self.get_serializer(
            data,
        )

        return Response(
            serializer.data,
        )
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.dashboard.services import (
    get_dashboard_data,
    get_recent_entries,
    get_recent_projects,
    get_upcoming_tasks,
)

from .serializers import (
    DashboardSerializer,
    DashboardRecentEntrySerializer,
    DashboardRecentProjectSerializer,
    DashboardUpcomingTaskSerializer,
)

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

    permission_classes = (
        IsAuthenticated,
    )

    serializer_class = DashboardSerializer

    def get(self, request):
        dashboard = get_dashboard_data(
            request.user,
        )

        serializer = self.get_serializer(
            {
                "summary": dashboard["summary"],
                "recent_entries": dashboard["recent_entries"],
                "top_projects": dashboard["top_projects"],
                "hours_per_day": dashboard["hours_per_day"],
                "billable_breakdown": dashboard["billable_breakdown"],
                "project_status_breakdown": dashboard["project_status_breakdown"],
                "charts": dashboard["charts"],
            }
        )

        return Response(
            serializer.data,
        )


class DashboardRecentEntriesAPIView(
    generics.GenericAPIView,
):
    """
    Return recent completed time entries.
    """

    permission_classes = (
        IsAuthenticated,
    )

    serializer_class = DashboardRecentEntrySerializer

    def get(
        self,
        request,
    ):
        entries = get_recent_entries(
            request.user,
        )

        serializer = self.get_serializer(
            entries,
            many=True,
        )

        return Response(
            serializer.data,
        )

class DashboardRecentProjectsAPIView(
    generics.GenericAPIView,
):
    """
    Return recently updated projects.
    """

    permission_classes = (
        IsAuthenticated,
    )

    serializer_class = (
        DashboardRecentProjectSerializer
    )

    def get(
        self,
        request,
    ):
        projects = get_recent_projects(
            request.user,
        )

        serializer = self.get_serializer(
            projects,
            many=True,
        )

        return Response(
            serializer.data,
        )

class DashboardUpcomingTasksAPIView(
    generics.GenericAPIView,
):
    """
    Return upcoming tasks.
    """

    permission_classes = (
        IsAuthenticated,
    )

    serializer_class = (
        DashboardUpcomingTaskSerializer
    )

    def get(
        self,
        request,
    ):
        tasks = get_upcoming_tasks(
            request.user,
        )

        serializer = self.get_serializer(
            tasks,
            many=True,
        )

        return Response(
            serializer.data,
        )
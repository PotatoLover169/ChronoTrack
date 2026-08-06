from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.notifications.services import (
    notify_project_created,
    notify_project_completed,
)
from apps.projects.models import Project

from .serializers import ProjectSerializer


class ProjectListCreateAPIView(
    generics.ListCreateAPIView,
):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(
            owner=self.request.user,
        )

    def perform_create(
        self,
        serializer,
    ):
        project = serializer.save(
            owner=self.request.user,
        )

        notify_project_created(
            recipient=self.request.user,
            project=project,
        )


class ProjectRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView,
):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(
            owner=self.request.user,
        )

    def perform_update(
        self,
        serializer,
    ):
        was_completed = (
            serializer.instance.status
            == "completed"
        )

        project = serializer.save()

        if (
            not was_completed
            and project.status == "completed"
        ):
            notify_project_completed(
                recipient=self.request.user,
                project=project,
            )
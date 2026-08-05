from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.notifications.services import (
    notify_task_created,
)
from apps.tasks.models import Task

from .serializers import TaskSerializer


class TaskListCreateAPIView(
    generics.ListCreateAPIView,
):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            owner=self.request.user,
        )

    def perform_create(
        self,
        serializer,
    ):
        task = serializer.save(
            owner=self.request.user,
        )

        notify_task_created(
            recipient=self.request.user,
            task=task,
        )


class TaskRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView,
):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            owner=self.request.user,
        )
from django.db import models
from rest_framework import generics

from apps.notifications.services import (
    notify_task_created,
    notify_task_completed,
)
from apps.tasks.models import Task

from .permissions import TaskPermission
from .serializers import TaskSerializer


def is_manager_or_admin(user):
    return (
        user.is_superuser
        or user.groups.filter(
            name__in=["Manager", "Admin"]
        ).exists()
    )


class TaskListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [TaskPermission]

    def get_queryset(self):
        user = self.request.user

        # Managers/Admins can see every task.
        if is_manager_or_admin(user):
            return Task.objects.all()

        # Employees can only see tasks assigned to them.
        return Task.objects.filter(
            assigned_to=user
        )

    def perform_create(self, serializer):
        task = serializer.save(
            owner=self.request.user
        )

        notify_task_created(
            recipient=self.request.user,
            task=task,
        )


class TaskRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = TaskSerializer
    permission_classes = [TaskPermission]

    def get_queryset(self):
        user = self.request.user

        # Managers/Admins can access every task.
        if is_manager_or_admin(user):
            return Task.objects.all()

        # Employees can only access tasks assigned to them.
        return Task.objects.filter(
            assigned_to=user
        )

    def perform_update(self, serializer):
        was_completed = (
            serializer.instance.status == "completed"
        )

        task = serializer.save()

        if (
            not was_completed
            and task.status == "completed"
        ):
            notify_task_completed(
                recipient=self.request.user,
                task=task,
            )
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.projects.models import Project
from .serializers import ProjectSerializer


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProjectRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)
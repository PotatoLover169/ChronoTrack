from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import (
    NoRunningTimerError,
    TimerAlreadyRunningError,
)
from .serializers import (
    CurrentTimerSerializer,
    StartTimerSerializer,
)
from .services import (
    get_current_timer,
    start_timer,
    stop_timer,
)

class StartTimerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StartTimerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            time_entry = start_timer(
                user=request.user,
                project=serializer.validated_data["project"],
                task=serializer.validated_data.get("task"),
                description=serializer.validated_data.get(
                    "description",
                    "",
                ),
            )

        except TimerAlreadyRunningError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {
                "message": "Timer started successfully.",
                "time_entry_id": time_entry.id,
            },
            status=status.HTTP_201_CREATED,
        )

class StopTimerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            time_entry = stop_timer(
                user=request.user,
            )

        except NoRunningTimerError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {
                "message": "Timer stopped successfully.",
                "time_entry_id": time_entry.id,
                "duration": str(time_entry.duration),
            },
            status=status.HTTP_200_OK,
        )

class CurrentTimerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        time_entry = get_current_timer(
            user=request.user,
        )

        if not time_entry:
            return Response(
                {
                    "detail": "No running timer.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CurrentTimerSerializer(
            time_entry,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
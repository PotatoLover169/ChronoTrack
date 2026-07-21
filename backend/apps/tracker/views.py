from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import TimerAlreadyRunningError
from .serializers import StartTimerSerializer
from .services import start_timer


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
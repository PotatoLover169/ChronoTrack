from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.approvals.exceptions import (
    PendingEditRequestExistsError,
)
from apps.approvals.services import (
    create_edit_request,
)

from .serializers import TimeEntryEditRequestSerializer


class CreateTimeEntryEditRequestView(APIView):
    permission_classes = (
        IsAuthenticated,
    )

    def post(self, request):
        serializer = TimeEntryEditRequestSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:
            edit_request = create_edit_request(
                user=request.user,
                **serializer.validated_data,
            )

        except PendingEditRequestExistsError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": (
                    "Time entry edit request submitted successfully."
                ),
                "edit_request_id": edit_request.id,
            },
            status=status.HTTP_201_CREATED,
        )
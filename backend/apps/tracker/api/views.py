from datetime import datetime

from django.core.exceptions import ValidationError

from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CurrentTimerSerializer,
    StartTimerSerializer,
    TimeEntrySerializer,
)

from ..exceptions import (
    NoRunningTimerError,
    TimerAlreadyRunningError,
)

from ..models import TimeEntry

from ..services import (
    get_current_timer,
    start_timer,
    stop_timer,
)


class StartTimerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StartTimerSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

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

        except ValidationError as exc:
            return Response(
                exc.message_dict,
                status=status.HTTP_400_BAD_REQUEST,
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


class TimeEntryListView(generics.ListAPIView):
    """
    Return time-entry history according to the user's role.

    Employee:
        Only their own time entries.

    Manager:
        All time entries.

    Admin:
        All time entries.

    Supported filters:
        ?project=<project_id>
        ?task=<task_id>
        ?status=<status>
        ?billable=true|false
        ?start_date=YYYY-MM-DD
        ?end_date=YYYY-MM-DD
    """

    serializer_class = TimeEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = TimeEntry.objects.select_related(
            "owner",
            "project",
            "task",
        )

        # --------------------------------------------------
        # 1. Establish the user's allowed data first.
        # --------------------------------------------------

        if user.is_superuser or user.groups.filter(
            name="Admin"
        ).exists():
            # Admin can see all time entries.
            pass

        elif user.groups.filter(
            name="Manager"
        ).exists():
            # Manager can see all time entries.
            pass

        else:
            # Employee can only see their own time entries.
            queryset = queryset.filter(
                owner=user,
            )

        # --------------------------------------------------
        # 2. Project filter.
        # --------------------------------------------------

        project_id = self.request.query_params.get(
            "project"
        )

        if project_id:
            queryset = queryset.filter(
                project_id=project_id,
            )

        # --------------------------------------------------
        # 3. Task filter.
        # --------------------------------------------------

        task_id = self.request.query_params.get(
            "task"
        )

        if task_id:
            queryset = queryset.filter(
                task_id=task_id,
            )

        # --------------------------------------------------
        # 4. Status filter.
        # --------------------------------------------------

        entry_status = self.request.query_params.get(
            "status"
        )

        if entry_status:
            queryset = queryset.filter(
                status=entry_status,
            )

        # --------------------------------------------------
        # 5. Billable filter.
        # --------------------------------------------------

        billable = self.request.query_params.get(
            "billable"
        )

        if billable is not None:
            if billable.lower() == "true":
                queryset = queryset.filter(
                    billable=True,
                )

            elif billable.lower() == "false":
                queryset = queryset.filter(
                    billable=False,
                )

            else:
                raise serializers.ValidationError(
                    {
                        "billable": (
                            "Use 'true' or 'false'."
                        )
                    }
                )

        # --------------------------------------------------
        # 6. Date filters.
        # --------------------------------------------------

        start_date_value = self.request.query_params.get(
            "start_date"
        )

        end_date_value = self.request.query_params.get(
            "end_date"
        )

        start_date = None
        end_date = None

        # --------------------------------------------------
        # 6a. Validate start_date.
        # --------------------------------------------------

        if start_date_value:
            try:
                start_date = datetime.strptime(
                    start_date_value,
                    "%Y-%m-%d",
                ).date()

            except ValueError:
                raise serializers.ValidationError(
                    {
                        "start_date": (
                            "Use the YYYY-MM-DD format."
                        )
                    }
                )

        # --------------------------------------------------
        # 6b. Validate end_date.
        # --------------------------------------------------

        if end_date_value:
            try:
                end_date = datetime.strptime(
                    end_date_value,
                    "%Y-%m-%d",
                ).date()

            except ValueError:
                raise serializers.ValidationError(
                    {
                        "end_date": (
                            "Use the YYYY-MM-DD format."
                        )
                    }
                )

        # --------------------------------------------------
        # 6c. Validate the date range.
        # --------------------------------------------------

        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError(
                    {
                        "date_range": (
                            "start_date cannot be later "
                            "than end_date."
                        )
                    }
                )

        # --------------------------------------------------
        # 6d. Apply start_date.
        # --------------------------------------------------

        if start_date:
            queryset = queryset.filter(
                start_time__date__gte=start_date,
            )

        # --------------------------------------------------
        # 6e. Apply end_date.
        # --------------------------------------------------

        if end_date:
            queryset = queryset.filter(
                start_time__date__lte=end_date,
            )

        # --------------------------------------------------
        # 7. Return newest entries first.
        # --------------------------------------------------

        return queryset.order_by(
            "-start_time"
        )


class TimeEntryDetailView(generics.RetrieveAPIView):
    """
    Return a single time entry according to the user's role.

    Employee:
        Only their own entries.

    Manager:
        All time entries.

    Admin:
        Any time entry.
    """

    serializer_class = TimeEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = TimeEntry.objects.select_related(
            "owner",
            "project",
            "task",
        )

        # --------------------------------------------------
        # Admin / superuser can access any entry.
        # --------------------------------------------------

        if user.is_superuser or user.groups.filter(
            name="Admin"
        ).exists():
            return queryset

        # --------------------------------------------------
        # Manager can access all time entries.
        # --------------------------------------------------

        if user.groups.filter(
            name="Manager"
        ).exists():
            return queryset

        # --------------------------------------------------
        # Employee can access only their own entries.
        # --------------------------------------------------

        return queryset.filter(
            owner=user,
        )
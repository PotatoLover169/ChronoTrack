from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response

from apps.reports.services import (
    get_report_summary,
    get_timesheet_report,
)

from .serializers import (
    ReportSummarySerializer,
    TimesheetReportSerializer,
)


class ReportSummaryView(
    generics.GenericAPIView,
):
    """
    Return a summary report for the authenticated user.
    """

    serializer_class = (
        ReportSummarySerializer
    )

    permission_classes = (
        IsAuthenticated,
    )

    def get(self, request):
        summary = get_report_summary(
            request.user,
        )

        serializer = self.get_serializer(
            summary,
        )

        return Response(
            serializer.data,
        )


class TimesheetReportView(
    generics.GenericAPIView,
):
    """
    Return completed time entries.
    """

    serializer_class = (
        TimesheetReportSerializer
    )

    permission_classes = (
        IsAuthenticated,
    )

    def get(self, request):
        start_date = request.query_params.get(
            "start_date",
        )

        end_date = request.query_params.get(
            "end_date",
        )

        project_id = request.query_params.get(
            "project",
        )

        client_id = request.query_params.get(
            "client",
        )

        billable = request.query_params.get(
            "billable",
        )

        if billable is not None:
            billable = (
                billable.lower() == "true"
            )

        entries = get_timesheet_report(
            user=request.user,
            start_date=start_date,
            end_date=end_date,
            project_id=project_id,
            client_id=client_id,
            billable=billable,
        )

        serializer = self.get_serializer(
            entries,
            many=True,
        )

        return Response(
            serializer.data,
        )
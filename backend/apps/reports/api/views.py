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
        entries = get_timesheet_report(
            request.user,
        )

        serializer = self.get_serializer(
            entries,
            many=True,
        )

        return Response(
            serializer.data,
        )
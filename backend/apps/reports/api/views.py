import csv

from django.http import HttpResponse

from openpyxl import Workbook
from openpyxl.styles import Font

from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response

from apps.reports.services import (
    get_daily_report,
    get_weekly_report,
    get_monthly_report,
    get_report_summary,
    get_timesheet_report,
    get_project_report,
    get_client_report,
    get_dashboard_analytics,
    get_productivity_analytics,
)

from .serializers import (
    DailyReportSerializer,
    WeeklyReportSerializer,
    MonthlyReportSerializer,
    ReportSummarySerializer,
    TimesheetReportSerializer,
    ProjectReportSerializer,
    ClientReportSerializer,
    DashboardAnalyticsSerializer,
    ProductivityAnalyticsSerializer,
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

class DailyReportView(
    generics.GenericAPIView,
):
    """
    Return today's report for the authenticated user.
    """

    serializer_class = (
        DailyReportSerializer
    )

    permission_classes = (
        IsAuthenticated,
    )

    def get(
        self,
        request,
    ):
        report = get_daily_report(
            user=request.user,
        )

        serializer = self.get_serializer(
            report,
        )

        return Response(
            serializer.data,
        )

class WeeklyReportView(
    generics.GenericAPIView,
):
    """
    Return this week's report for the authenticated user.
    """

    serializer_class = (
        WeeklyReportSerializer
    )

    permission_classes = (
        IsAuthenticated,
    )

    def get(
        self,
        request,
    ):
        report = get_weekly_report(
            user=request.user,
        )

        serializer = self.get_serializer(
            report,
        )

        return Response(
            serializer.data,
        )

class MonthlyReportView(
    generics.GenericAPIView,
):
    """
    Return this month's report for the authenticated user.
    """

    serializer_class = (
        MonthlyReportSerializer
    )

    permission_classes = (
        IsAuthenticated,
    )

    def get(
        self,
        request,
    ):
        report = get_monthly_report(
            user=request.user,
        )

        serializer = self.get_serializer(
            report,
        )

        return Response(
            serializer.data,
        )

class ProjectReportView(
    generics.GenericAPIView,
):
    """
    Return report for a specific project.
    """

    serializer_class = (
        ProjectReportSerializer
    )

    permission_classes = (
        IsAuthenticated,
    )

    def get(
        self,
        request,
        project_id,
    ):
        report = get_project_report(
            user=request.user,
            project_id=project_id,
        )

        serializer = self.get_serializer(
            report,
        )

        return Response(
            serializer.data,
        )

class ClientReportView(
    generics.GenericAPIView,
):
    """
    Return a report for a specific client.
    """

    serializer_class = (
        ClientReportSerializer
    )

    permission_classes = (
        IsAuthenticated,
    )

    def get(
        self,
        request,
        client_id,
    ):
        report = get_client_report(
            user=request.user,
            client_id=client_id,
        )

        serializer = self.get_serializer(
            report,
        )

        return Response(
            serializer.data,
        )

class DashboardAnalyticsView(
    generics.GenericAPIView,
):
    """
    Return dashboard analytics for the authenticated user.
    """

    serializer_class = (
        DashboardAnalyticsSerializer
    )

    permission_classes = (
        IsAuthenticated,
    )

    def get(
        self,
        request,
    ):
        analytics = get_dashboard_analytics(
            user=request.user,
        )

        serializer = self.get_serializer(
            analytics,
        )

        return Response(
            serializer.data,
        )

class ProductivityAnalyticsView(
    generics.GenericAPIView,
):
    """
    Return productivity analytics.
    """

    serializer_class = (
        ProductivityAnalyticsSerializer
    )

    permission_classes = (
        IsAuthenticated,
    )

    def get(
        self,
        request,
    ):
        data = get_productivity_analytics(
            user=request.user,
        )

        serializer = self.get_serializer(
            data,
            many=True,
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

class TimesheetCSVExportView(
    generics.GenericAPIView,
):
    """
    Export completed time entries as CSV.
    """

    permission_classes = (
        IsAuthenticated,
    )

    def get(self, request):

        start_date = request.GET.get(
            "start_date"
        )

        end_date = request.GET.get(
            "end_date"
        )

        project_id = request.GET.get(
            "project"
        )

        client_id = request.GET.get(
            "client"
        )

        billable = request.GET.get(
            "billable"
        )

        ordering = request.GET.get(
            "ordering",
            "-start_time",
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
            ordering=ordering,
        )

        response = HttpResponse(
            content_type="text/csv",
        )

        response[
            "Content-Disposition"
        ] = (
            'attachment; filename="timesheet_report.csv"'
        )

        writer = csv.writer(
            response,
        )

        writer.writerow([
            "Project",
            "Task",
            "Date",
            "Start Time",
            "End Time",
            "Duration",
            "Billable",
            "Hourly Rate",
            "Earnings",
        ])

        for entry in entries:

            writer.writerow([
                entry.project.name,
                entry.task.title if entry.task else "",
                entry.start_time.strftime("%Y-%m-%d"),
                entry.start_time.strftime("%H:%M"),
                entry.end_time.strftime("%H:%M") if entry.end_time else "",
                str(entry.duration)[:-3] if entry.duration else "",
                "Yes" if entry.billable else "No",
                f"{entry.hourly_rate:.2f}",
                f"{entry.earnings:.2f}",
            ])

        return response

class TimesheetExcelExportView(
    generics.GenericAPIView,
):
    """
    Export completed time entries as Excel.
    """

    permission_classes = (
        IsAuthenticated,
    )

    def get(self, request):

        start_date = request.GET.get(
            "start_date",
        )

        end_date = request.GET.get(
            "end_date",
        )

        project_id = request.GET.get(
            "project",
        )

        client_id = request.GET.get(
            "client",
        )

        billable = request.GET.get(
            "billable",
        )

        ordering = request.GET.get(
            "ordering",
            "-start_time",
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
            ordering=ordering,
        )

        workbook = Workbook()

        worksheet = workbook.active

        worksheet.title = "Timesheet Report"

        headers = [
            "Project",
            "Task",
            "Date",
            "Start Time",
            "End Time",
            "Duration",
            "Billable",
            "Hourly Rate",
            "Earnings",
        ]

        worksheet.append(headers)

        for cell in worksheet[1]:
            cell.font = Font(bold=True)

        for entry in entries:

            worksheet.append([
                entry.project.name,
                entry.task.title if entry.task else "",
                entry.start_time.strftime("%Y-%m-%d"),
                entry.start_time.strftime("%H:%M"),
                entry.end_time.strftime("%H:%M")
                if entry.end_time else "",
                str(entry.duration)[:-3]
                if entry.duration else "",
                "Yes" if entry.billable else "No",
                float(entry.hourly_rate),
                float(entry.earnings),
            ])

        response = HttpResponse(
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        )

        response[
            "Content-Disposition"
        ] = (
            'attachment; filename="timesheet_report.xlsx"'
        )

        workbook.save(
            response,
        )

        return response
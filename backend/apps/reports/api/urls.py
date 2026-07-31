from django.urls import path

from .views import (
    DailyReportView,
    ReportSummaryView,
    TimesheetReportView,
    TimesheetCSVExportView,
    TimesheetExcelExportView,
)

urlpatterns = [
    path(
        "summary/",
        ReportSummaryView.as_view(),
        name="report-summary",
    ),
    path(
        "timesheet/",
        TimesheetReportView.as_view(),
        name="timesheet-report",
    ),
    path(
        "timesheet/export/csv/",
        TimesheetCSVExportView.as_view(),
        name="timesheet-csv-export",
    ),
    path(
        "timesheet/export/excel/",
        TimesheetExcelExportView.as_view(),
        name="timesheet-excel-export",
        ),

    path(
        "me/daily/",
        DailyReportView.as_view(),
        name="daily-report",
),
]
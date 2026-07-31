from django.urls import path

from .views import (
    DailyReportView,
    WeeklyReportView,
    MonthlyReportView,
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

    path(
        "me/weekly/",
        WeeklyReportView.as_view(),
        name="weekly-report",
        ),
    
    path(
        "me/monthly/",
        MonthlyReportView.as_view(),
        name="monthly-report",
        ),
]
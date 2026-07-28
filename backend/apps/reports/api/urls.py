from django.urls import path

from .views import (
    ReportSummaryView,
    TimesheetReportView,
    TimesheetCSVExportView,

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
]
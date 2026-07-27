from django.urls import path

from .views import (
    ReportSummaryView,
    TimesheetReportView,
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
]
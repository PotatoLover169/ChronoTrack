from django.urls import path

from .views import (
    CreateTimeEntryEditRequestView,
)

urlpatterns = [
    path(
        "time-entry-edit-requests/",
        CreateTimeEntryEditRequestView.as_view(),
        name="create-time-entry-edit-request",
    ),
]
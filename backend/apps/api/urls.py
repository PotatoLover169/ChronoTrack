from django.urls import include, path

urlpatterns = [
    # Dashboard API
    path("dashboard/", include("apps.dashboard.api.urls")),

    # Authentication API
    path("auth/", include("apps.accounts.api.urls")),
]
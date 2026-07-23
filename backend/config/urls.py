from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # Central API Router
    path("api/", include("apps.api.urls")),

    path("api/approvals/",
    include("apps.approvals.api.urls"),),
]
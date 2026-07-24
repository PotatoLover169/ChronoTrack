from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    MeAPIView,
    RegisterAPIView,
    UpdateProfileAPIView,
)
from .views_login import LoginAPIView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("me/", MeAPIView.as_view(), name="me"),

    path(
        "profile/",
        UpdateProfileAPIView.as_view(),
        name="update-profile",
    ),
]
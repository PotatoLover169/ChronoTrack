from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny


class LoginAPIView(TokenObtainPairView):
    permission_classes = [AllowAny]
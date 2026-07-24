from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    RegisterSerializer,
    UpdateProfileSerializer,
    UserSerializer,
)

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UpdateProfileAPIView(generics.UpdateAPIView):
    """
    Update the authenticated user's profile.
    """

    serializer_class = UpdateProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.reports.services import get_report_summary

from .serializers import ReportSummarySerializer


class ReportSummaryView(generics.GenericAPIView):
    """
    Return a summary report for the authenticated user.
    """

    serializer_class = ReportSummarySerializer

    permission_classes = (
        IsAuthenticated,
    )

    def get(self, request):
        summary = get_report_summary(
            request.user,
        )

        serializer = self.get_serializer(
            summary,
        )

        return Response(
            serializer.data,
        )
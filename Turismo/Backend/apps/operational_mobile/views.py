from rest_framework import viewsets, permissions
from .models import Operator, OperatorTracking, OperationReport
from .serializers import OperatorSerializer, OperatorTrackingSerializer, OperationReportSerializer

class OperatorViewSet(viewsets.ModelViewSet):
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer
    permission_classes = [permissions.IsAuthenticated]

class OperatorTrackingViewSet(viewsets.ModelViewSet):
    queryset = OperatorTracking.objects.all()
    serializer_class = OperatorTrackingSerializer
    permission_classes = [permissions.IsAuthenticated]

class OperationReportViewSet(viewsets.ModelViewSet):
    queryset = OperationReport.objects.all()
    serializer_class = OperationReportSerializer
    permission_classes = [permissions.IsAuthenticated]

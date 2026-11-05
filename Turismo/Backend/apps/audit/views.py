from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import ForensicSecurityLog
from .serializers import ForensicSecurityLogSerializer

class ForensicSecurityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ForensicSecurityLog.objects.all()
    serializer_class = ForensicSecurityLogSerializer
    permission_classes = [IsAdminUser]

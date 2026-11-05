# automation/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Workflow, AgentPersona
from .serializers import WorkflowDetailSerializer, WorkflowCreateSerializer, AgentPersonaSerializer
import logging

logger = logging.getLogger(__name__)

class AgentPersonaViewSet(viewsets.ModelViewSet):
    queryset = AgentPersona.objects.all()
    serializer_class = AgentPersonaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)

class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return WorkflowCreateSerializer
        return WorkflowDetailSerializer

    def get_queryset(self):
        return Workflow.objects.filter(tenant=self.request.user.tenant)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        if not serializer.data:
            logger.info(f"No workflows found for tenant {request.user.tenant.id}")
            return Response({
                "data": [],
                "meta": {
                    "count": 0,
                    "tenant_id": request.user.tenant.id,
                    "reason": "NO_DATA"
                }
            })

        return Response({
            "data": serializer.data,
            "meta": {
                "count": len(serializer.data),
                "tenant_id": request.user.tenant.id
            }
        })

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)

from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema
from .models import LegacyCustodian, LegacyMilestone, LegacyGuardrail
from .serializers import LegacyCustodianSerializer, LegacyMilestoneSerializer, LegacyGuardrailSerializer

class LegacyDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = LegacyMilestoneSerializer # Fallback

    @extend_schema(responses={200: serializers.JSONField()})
    def list(self, request):
        custodians = LegacyCustodian.objects.filter(is_active=True).count()
        milestones = LegacyMilestone.objects.all().order_by('-timestamp')[:10]
        guardrails = LegacyGuardrail.objects.filter(is_active=True)

        return Response({
            "status": "LEGADO_PROTEGIDO",
            "active_custodians": custodians,
            "recent_milestones": LegacyMilestoneSerializer(milestones, many=True).data,
            "active_guardrails": LegacyGuardrailSerializer(guardrails, many=True).data
        })

class LegacyMilestoneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LegacyMilestone.objects.all().order_by('-timestamp')
    serializer_class = LegacyMilestoneSerializer
    permission_classes = [IsAdminUser]

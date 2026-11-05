from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SaaSSubscription, CommercialKPI, SaaSInvoice
from .lead_model import SaaSLead
from .plan_model import SaaSPlan
from .serializers import (
    SaaSLeadSerializer, SaaSSubscriptionSerializer,
    CommercialKPISerializer, SaaSPlanSerializer,
    SaaSInvoiceSerializer
)
from .pipeline_engine import PipelineEngine
from .conversion_orchestrator import ConversionOrchestrator

class SaaSLeadViewSet(viewsets.ModelViewSet):
    queryset = SaaSLead.objects.all().order_by('-created_at')
    serializer_class = SaaSLeadSerializer

    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        lead = self.get_object()
        new_status = request.data.get('status')
        reason = request.data.get('reason')

        if new_status not in [s[0] for s in SaaSLead.Status.choices]:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        PipelineEngine.transition_to(lead, new_status, reason)
        return Response(SaaSLeadSerializer(lead).data)

    @action(detail=True, methods=['post'])
    def convert(self, request, pk=None):
        plan_id = request.data.get('plan_id')
        billing_cycle = request.data.get('billing_cycle', 'MONTHLY')

        if not plan_id:
            return Response({'error': 'plan_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        result = ConversionOrchestrator.convert_lead_to_subscription(
            lead_id=str(pk),
            plan_id=plan_id,
            billing_cycle=billing_cycle
        )

        if result['status'] == 'SUCCESS':
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

class SaaSSubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SaaSSubscription.objects.all().order_by('-start_date')
    serializer_class = SaaSSubscriptionSerializer

class CommercialKPIViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommercialKPI.objects.all().order_by('-timestamp')
    serializer_class = CommercialKPISerializer

    @action(detail=False, methods=['get'])
    def latest(self, request):
        metrics = ['MRR', 'ARR', 'CONVERSION_RATE']
        latest_data = {}
        for metric in metrics:
            kpi = CommercialKPI.objects.filter(metric_name=metric).first()
            if kpi:
                latest_data[metric] = kpi.value
        return Response(latest_data)

class SaaSPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SaaSPlan.objects.filter(is_active=True)
    serializer_class = SaaSPlanSerializer

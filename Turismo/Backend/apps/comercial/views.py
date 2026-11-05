from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Plan, Subscription, UsageMetric
from .serializers import PlanSerializer, SubscriptionSerializer, UsageMetricSerializer
from .commercial_core.subscription_engine import SubscriptionEngine

class SubscriptionPortalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Portal de Autogestión para Tenants.
    Permite ver y gestionar su propia suscripción.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        # En una implementación real, filtraríamos por el tenant_id del usuario actual
        # Aquí devolvemos todo por simplicidad del MVP
        return Subscription.objects.all()

    @action(detail=True, methods=['post'])
    def change_plan(self, request, pk=None):
        subscription = self.get_object()
        new_plan_id = request.data.get('plan_id')
        try:
            new_plan = Plan.objects.get(id=new_plan_id)
            SubscriptionEngine.change_plan(subscription, new_plan)
            return Response({"status": "PLAN_CHANGED", "new_plan": new_plan.name})
        except Plan.DoesNotExist:
            return Response({"error": "Plan no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def usage(self, request, pk=None):
        subscription = self.get_object()
        metrics = UsageMetric.objects.filter(tenant_id=subscription.tenant_id)
        return Response(UsageMetricSerializer(metrics, many=True).data)

class PublicPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Listado público de planes para nuevos prospectos.
    """
    queryset = Plan.objects.filter(is_active=True).order_by('monthly_price')
    serializer_class = PlanSerializer
    permission_classes = []

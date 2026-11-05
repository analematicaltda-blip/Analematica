from rest_framework import viewsets, permissions, views, response
from .domain.kpi import KPI
from .domain.alert import Alert
from .domain.threshold import Threshold
from .serializers import KPISerializer, AlertSerializer, ThresholdSerializer, ExecutiveDashboardSerializer
from apps.admin_plataforma.mixins import SystemicERPViewSetMixin
from api.permissions import IsSuperAdmin
from django.db.models import Sum
from decimal import Decimal

class KPIViewSet(SystemicERPViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = KPI.objects.all()
    serializer_class = KPISerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class AlertViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class ThresholdViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = Threshold.objects.all()
    serializer_class = ThresholdSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class ExecutiveDashboardView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        tenant_id = request.query_params.get('tenant_id')

        kpis = KPI.objects.all()
        alerts = Alert.objects.filter(status='OPEN')

        if tenant_id:
            kpis = kpis.filter(tenant_id=tenant_id)
            alerts = alerts.filter(tenant_id=tenant_id)

        # Aggregation
        total_revenue = kpis.filter(name='DAILY_REVENUE').aggregate(total=Sum('value'))['total'] or Decimal('0.00')
        net_profit = kpis.filter(name='DAILY_NET_PROFIT').aggregate(total=Sum('value'))['total'] or Decimal('0.00')

        # Executive Mode metrics
        ebitda = kpis.filter(name='EBITDA').first()
        burn_rate = kpis.filter(name='BURN_RATE').first()
        systemic_risk = kpis.filter(name='SYSTEMIC_RISK').first()

        data = {
            "total_revenue": total_revenue,
            "net_profit": net_profit,
            "ebitda": ebitda.value if ebitda else 0,
            "burn_rate": burn_rate.value if burn_rate else 0,
            "systemic_risk": systemic_risk.value if systemic_risk else 0,
            "open_alerts_count": alerts.count(),
            "kpi_snapshots": kpis[:10],
            "recent_alerts": alerts[:5]
        }

        # ViewModel Integration (Phase 2)
        from .view_models.executive_snapshot import ExecutiveSnapshot
        from .view_models.intention_feed import IntentionFeed
        from .view_models.systemic_risk_view import SystemicRiskView

        snapshot = ExecutiveSnapshot.get_latest()

        data.update({
            "executive_summary": {
                "active_proposals": snapshot.active_proposals,
                "infra_status": snapshot.infra_status,
                "systemic_risk_score": snapshot.systemic_risk
            },
            "risk_heatmap": SystemicRiskView.get_risk_context(),
            "governance_feed": IntentionFeed.get_recent_intentions(limit=10)
        })

        # Note: We return the data directly as it's a multi-viewModel composite
        return response.Response(data)

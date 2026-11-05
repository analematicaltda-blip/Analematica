from django.db.models import Sum, Count
from ..models import Lead
from ..models import Subscription
from ..models import Plan

class DashboardService:
    """
    Servicio de Inteligencia de Negocio para el Super Admin.
    """

    @staticmethod
    def get_commercial_kpis():
        """Retorna métricas clave del sistema SaaS."""
        active_subs = Subscription.objects.filter(status=Subscription.Status.ACTIVE)
        total_mrr = active_subs.aggregate(total=Sum('plan__monthly_price'))['total'] or 0

        return {
            "leads": {
                "total": Lead.objects.count(),
                "hot_leads": Lead.objects.filter(score__gte=75).count()
            },
            "subscriptions": {
                "active": active_subs.count(),
                "total_mrr": total_mrr,
                "arr": total_mrr * 12
            },
            "plans": {
                "distribution": Plan.objects.annotate(count=Count('saassubscription')).values('name', 'count')
            }
        }

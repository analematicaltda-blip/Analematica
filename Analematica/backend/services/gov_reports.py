from celery import shared_task
from django.db.models import Sum, Count, Avg
from apps.api.models import CustomUser, GovernmentProfile
from apps.prestadores.models import # assume

@shared_task
def update_muni_report(muni_code):
    # Aggregate 40 KPIs from sales/reservas etc.
    data = {}
    data['ventas_diarias'] = # query
    # 40 items...
    cache.set(f'report_muni_{muni_code}', data)


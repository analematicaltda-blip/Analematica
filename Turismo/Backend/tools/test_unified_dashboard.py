import os
import django
import json
from uuid import UUID

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from apps.tourism_intelligence.api.views import IntelligenceViewSet
from django.contrib.auth import get_user_model
from apps.turismo.models.provider_models import TourismProvider
from apps.tourism_intelligence.models import TourismDemandForecast, TourismEconomicImpact
from decimal import Decimal

User = get_user_model()

def run_test():
    print("Iniciando prueba de Dashboard Unificado...")

    # 1. Asegurar datos básicos
    admin, _ = User.objects.get_or_create(username='admin_audit', is_staff=True, is_superuser=True)

    # Asegurar al menos un forecast y un impacto
    TourismDemandForecast.objects.get_or_create(
        destino='Puerto Gaitán',
        categoria_servicio='ACCOMMODATION',
        fecha='2026-04-01',
        defaults={'demanda_estimada': 150}
    )

    TourismEconomicImpact.objects.get_or_create(
        destino='Puerto Gaitán',
        periodo='2026-Q1',
        defaults={
            'ventas_totales': Decimal('50000.00'),
            'ingresos_turisticos_netos': Decimal('45000.00')
        }
    )

    # 2. Simular petición
    factory = APIRequestFactory()
    view = IntelligenceViewSet.as_view({'get': 'dashboard'})
    request = factory.get('/api/v1/tourism/intelligence/dashboard/')
    force_authenticate(request, user=admin)

    response = view(request)

    print(f"Status Code: {response.status_code}")
    print("Response Data:")
    print(json.dumps(response.data, indent=2, cls=UUIDEncoder))

    if response.status_code == 200 and "via_3" in response.data:
        print("\n✅ PRUEBA EXITOSA: Dashboard Unificado operativo.")
    else:
        print("\n❌ FALLO: El dashboard no retornó la estructura esperada.")

if __name__ == "__main__":
    run_test()

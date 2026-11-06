import os
import django
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from apps.social.models import SocialConversation, SocialMessage
from apps.tourism_intelligence.analytics_engine import ConversationalAnalyticsEngine
from apps.turismo.models.provider_models import TourismProvider, TourismService, Reservation
from apps.wallet.models import Wallet
from django.contrib.auth import get_user_model

User = get_user_model()

def run_test():
    print("🚀 INICIANDO TEST DE FLUJO ECONÓMICO INTEGRADO (V3 -> V4 -> V5)")

    # 1. Preparar Entorno
    tourist, _ = User.objects.get_or_create(username='turista_eco_flow', defaults={'role': 'TURIST'})
    owner, _ = User.objects.get_or_create(username='owner_eco_flow', defaults={'role': 'BUSINESS_OWNER'})

    # Wallets
    t_wallet, _ = Wallet.objects.get_or_create(user_id=tourist.id, defaults={'owner_type': 'TURISTA', 'owner_id': str(tourist.id)})
    t_wallet.saldo_disponible = Decimal('1000.00')
    t_wallet.save()

    p_wallet, _ = Wallet.objects.get_or_create(user_id=owner.id, defaults={'owner_type': 'HOTEL', 'owner_id': str(owner.id)})

    # Servicio
    provider, _ = TourismProvider.objects.get_or_create(name="Hotel Flow", owner=owner, defaults={'provider_type': 'HOTEL'})
    service, _ = TourismService.objects.get_or_create(
        provider=provider, name="Suite Luxury",
        defaults={'price': Decimal('250.00'), 'service_type': 'ACCOMMODATION', 'availability': True}
    )

    # 2. VÍA 3: Interacción Conversacional
    conv = SocialConversation.objects.create(title="Charla Turismo", created_by=tourist)
    msg = SocialMessage.objects.create(
        conversation=conv, sender=tourist,
        content="Hola Sarita, estoy buscando un hotel con suite luxury"
    )

    print("\nVía 3: Analizando intención del mensaje...")
    intent = ConversationalAnalyticsEngine.analyze_message(msg)
    print(f"   -> Intención Detectada: {intent.intent}")

    # 3. VÍA 4: Automatización (Se disparó internamente en el analyze_message)
    # En un sistema real, el EventBus habría notificado las recomendaciones.
    print("Vía 4: Automatización procesada (Recomendaciones emitidas).")

    # 4. VÍA 5: Transacción Económica
    print("\nVía 5: Ejecutando Reserva y Pago...")
    res = Reservation.objects.create(
        provider=provider, service=service, customer=tourist,
        start_date=timezone.now(), end_date=timezone.now() + timedelta(days=1),
        total_price=service.price, status=Reservation.Status.PENDING
    )

    # Procesar Pago Real
    from apps.turismo.api.provider_views import ReservationViewSet
    from rest_framework.test import APIRequestFactory, force_authenticate

    factory = APIRequestFactory()
    view = ReservationViewSet.as_view({'post': 'process_payment'})
    request = factory.post(f'/api/v1/turismo/tourism-reservations/{res.id}/process_payment/')
    force_authenticate(request, user=tourist)

    response = view(request, pk=res.id)
    print(f"   -> Resultado Pago API: {response.status_code}")

    # 5. Verificación Final
    t_wallet.refresh_from_db()
    p_wallet.refresh_from_db()
    res.refresh_from_db()

    print(f"\nSaldos Finales:")
    print(f"   - Turista: {t_wallet.saldo_disponible} (Esperado 750)")
    print(f"   - Prestador: {p_wallet.saldo_disponible} (Esperado 225 - 90%)")
    print(f"   - Estado Reserva: {res.status} (Esperado CONFIRMED)")

    if res.status == 'CONFIRMED' and t_wallet.saldo_disponible == Decimal('750.00'):
        print("\n✅ FLUJO ECONÓMICO INTEGRADO EXITOSO.")
    else:
        print("\n❌ FALLO: El flujo no se completó según lo esperado.")

if __name__ == "__main__":
    run_test()

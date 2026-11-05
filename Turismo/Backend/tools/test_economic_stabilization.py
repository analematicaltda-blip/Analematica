import os
import django
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from apps.turismo.models.provider_models import TourismProvider, TourismService, Reservation
from apps.wallet.models import Wallet, WalletTransaccion, WalletMovimiento
from apps.wallet.services.wallet_service import WalletService
from django.contrib.auth import get_user_model

User = get_user_model()

def run_test():
    print("Iniciando Prueba de Estabilización Económica...")

    # 1. Preparar usuarios y carteras (Limpiar saldos para el test)
    tourist, _ = User.objects.get_or_create(username='tourist_eco', defaults={'role': 'TURIST'})
    owner, _ = User.objects.get_or_create(username='owner_eco', defaults={'role': 'BUSINESS_OWNER'})

    # Reset saldos
    t_wallet, _ = Wallet.objects.get_or_create(user_id=tourist.id, defaults={'owner_type': 'TURISTA', 'owner_id': str(tourist.id)})
    t_wallet.saldo_disponible = Decimal('500.00')
    t_wallet.save()

    o_wallet, _ = Wallet.objects.get_or_create(user_id=owner.id, defaults={'owner_type': 'HOTEL', 'owner_id': str(owner.id)})
    o_wallet.saldo_disponible = Decimal('0.00')
    o_wallet.save()

    h_wallet, _ = Wallet.objects.get_or_create(owner_id='SARITA-HOLDING', defaults={'owner_type': 'CORPORATIVO'})
    # No reseteamos holding para ver acumulado o simplemente anotamos el previo
    prev_h_saldo = h_wallet.saldo_disponible

    # 2. Crear un servicio y una reserva
    provider, _ = TourismProvider.objects.get_or_create(name="Eco Lodge", owner=owner, defaults={'provider_type': 'HOTEL'})
    service, _ = TourismService.objects.get_or_create(
        provider=provider, name="Suite Selva",
        defaults={'price': Decimal('100.00'), 'service_type': 'ACCOMMODATION'}
    )

    res = Reservation.objects.create(
        provider=provider, service=service, customer=tourist,
        start_date=timezone.now(), end_date=timezone.now() + timedelta(days=1),
        total_price=Decimal('100.00'), status=Reservation.Status.PENDING
    )

    print(f"Reserva creada: {res.id} - Monto: {res.total_price}")

    # 3. Simular el pago via WalletService
    ws = WalletService(user=tourist)
    try:
        # PAGO DE 100 -> 90 al prestador, 10 al holding
        tx = ws.pay_to_user(target_user=owner, amount=res.total_price, related_service_id=res.id, description="Pago Suite")
        print(f"✅ Transacción Wallet exitosa: {tx.id}")

        # Verificar saldos
        t_wallet.refresh_from_db()
        o_wallet.refresh_from_db()
        h_wallet.refresh_from_db()

        print(f"Saldo Turista: {t_wallet.saldo_disponible} (Esperado 400)")
        print(f"Saldo Dueño: {o_wallet.saldo_disponible} (Esperado 90)")
        print(f"Incremento Holding: {h_wallet.saldo_disponible - prev_h_saldo} (Esperado 10)")

        if (t_wallet.saldo_disponible == Decimal('400.00') and
            o_wallet.saldo_disponible == Decimal('90.00') and
            (h_wallet.saldo_disponible - prev_h_saldo) == Decimal('10.00')):
            print("\n✅ ESTABILIZACIÓN ECONÓMICA CERTIFICADA.")
        else:
            print("\n❌ ERROR: Los saldos no coinciden con lo esperado (Posible fallo en comisión).")

    except Exception as e:
        print(f"❌ FALLO en transacción: {e}")

if __name__ == "__main__":
    run_test()

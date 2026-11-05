import os
import django
from decimal import Decimal

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from apps.wallet.models import Wallet, WalletTransaccion, WalletMovimiento
from apps.wallet.services.wallet_service import WalletService
from django.contrib.auth import get_user_model

User = get_user_model()

def run_test():
    print("Iniciando Prueba del Motor de Monetización...")

    # 1. Preparar actores
    tourist, _ = User.objects.get_or_create(username='tourist_mon', defaults={'role': 'TURIST'})
    provider_owner, _ = User.objects.get_or_create(username='owner_mon', defaults={'role': 'BUSINESS_OWNER'})

    t_wallet, _ = Wallet.objects.get_or_create(user_id=tourist.id, defaults={'owner_type': 'TURISTA', 'owner_id': str(tourist.id)})
    t_wallet.saldo_disponible = Decimal('100.00')
    t_wallet.save()

    p_wallet, _ = Wallet.objects.get_or_create(user_id=provider_owner.id, defaults={'owner_type': 'HOTEL', 'owner_id': str(provider_owner.id)})
    p_wallet.saldo_disponible = Decimal('0.00')
    p_wallet.save()

    # Asegurar wallet de holding
    h_wallet, _ = Wallet.objects.get_or_create(owner_id='SARITA-HOLDING', defaults={'owner_type': 'CORPORATIVO'})
    h_wallet.saldo_disponible = Decimal('0.00')
    h_wallet.save()

    # 2. Ejecutar pago de 00
    # Esperado: Turista -100, Prestador +90, Holding +10 (10% comisión)
    ws = WalletService(user=tourist)
    print("Ejecutando pago de 00.00 con comisión del 10%...")
    tx = ws.pay(to_wallet_id=str(p_wallet.id), amount=100.00, related_service_id="SVC-001", description="Test Monetización")

    # 3. Verificar resultados
    t_wallet.refresh_from_db()
    p_wallet.refresh_from_db()
    h_wallet.refresh_from_db()

    print(f"Saldo Turista: {t_wallet.saldo_disponible} (Esperado 0)")
    print(f"Saldo Prestador: {p_wallet.saldo_disponible} (Esperado 90)")
    print(f"Saldo Holding: {h_wallet.saldo_disponible} (Esperado 10)")

    if (t_wallet.saldo_disponible == Decimal('0.00') and
        p_wallet.saldo_disponible == Decimal('90.00') and
        h_wallet.saldo_disponible == Decimal('10.00')):
        print("\n✅ MOTOR DE MONETIZACIÓN CERTIFICADO.")
    else:
        print("\n❌ ERROR: La distribución de fondos es incorrecta.")

if __name__ == "__main__":
    run_test()

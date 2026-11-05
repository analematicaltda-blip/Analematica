import uuid
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
from apps.wallet.models import Wallet, WalletTransaccion, WalletMovimiento
from apps.wallet.services import WalletService
from api.models import CustomUser
from django.db import connection

def run_reality_test_17():
    print("🚀 INICIANDO TEST DE REALIDAD FASE 17 - MONEDERO SOBERANO")

    # 1. Preparación de Usuarios y Wallets
    admin = CustomUser.objects.filter(is_superuser=True).first()
    if not admin:
        admin = CustomUser.objects.create_superuser('admin_wallet', 'admin@test.com', 'password')

    cliente = CustomUser.objects.create_user(username=f'cliente_{uuid.uuid4().hex[:4]}', password='password')
    agencia_user = CustomUser.objects.create_user(username=f'agencia_{uuid.uuid4().hex[:4]}', password='password')
    hotel_user = CustomUser.objects.create_user(username=f'hotel_{uuid.uuid4().hex[:4]}', password='password')
    guia_user = CustomUser.objects.create_user(username=f'guia_{uuid.uuid4().hex[:4]}', password='password')

    # Los wallets se crean via signal con saldo 0
    wallet_cliente = Wallet.objects.get(user=cliente)
    wallet_agencia = Wallet.objects.get(user=agencia_user)
    wallet_hotel = Wallet.objects.get(user=hotel_user)
    wallet_guia = Wallet.objects.get(user=guia_user)

    service_admin = WalletService(user=admin)
    service_admin.deposit(wallet_cliente.id, Decimal('1000.00'), description="Carga inicial test")

    service = WalletService(user=cliente)

    print(f"✅ Escenario 1: Pago de Paquete Multi-Proveedor (Total: 500)")

    movements = [
        {"wallet_id": str(wallet_cliente.id), "monto": 500, "tipo": WalletMovimiento.TipoMovimiento.PAGO, "referencia_modelo": "Package", "referencia_id": "PKG-001"},
        {"wallet_id": str(wallet_hotel.id), "monto": 300, "tipo": WalletMovimiento.TipoMovimiento.INGRESO, "referencia_modelo": "Service", "referencia_id": "HOTEL-001"},
        {"wallet_id": str(wallet_guia.id), "monto": 100, "tipo": WalletMovimiento.TipoMovimiento.INGRESO, "referencia_modelo": "Service", "referencia_id": "GUIA-001"},
        {"wallet_id": str(wallet_agencia.id), "monto": 100, "tipo": WalletMovimiento.TipoMovimiento.INGRESO, "referencia_modelo": "Commission", "referencia_id": "AGENCY-001"},
    ]

    tx = service.execute_complex_transaction(referencia="BOOKING-PKG-001", movements_data=movements)

    wallet_cliente.refresh_from_db()
    wallet_hotel.refresh_from_db()
    wallet_guia.refresh_from_db()
    wallet_agencia.refresh_from_db()

    assert wallet_cliente.saldo_disponible == Decimal('500.00')
    assert wallet_hotel.saldo_disponible == Decimal('300.00')
    assert wallet_guia.saldo_disponible == Decimal('100.00')
    assert wallet_agencia.saldo_disponible == Decimal('100.00')
    print("   -> OK: Saldos distribuidos correctamente.")

    print(f"✅ Escenario 2: Reversión Parcial Compensatoria")
    compensatory_movements = [
        {"wallet_id": str(wallet_guia.id), "monto": 100, "tipo": WalletMovimiento.TipoMovimiento.LIQUIDACION, "referencia_modelo": "Refund", "referencia_id": "GUIA-001-REV"},
        {"wallet_id": str(wallet_cliente.id), "monto": 100, "tipo": WalletMovimiento.TipoMovimiento.INGRESO, "referencia_modelo": "Refund", "referencia_id": "GUIA-001-REV"},
    ]
    service_admin = WalletService(user=admin)
    service_admin.execute_complex_transaction(referencia="REFUND-GUIA-001", movements_data=compensatory_movements)

    wallet_cliente.refresh_from_db()
    wallet_guia.refresh_from_db()
    assert wallet_cliente.saldo_disponible == Decimal('600.00')
    assert wallet_guia.saldo_disponible == Decimal('0.00')
    print("   -> OK: Reversión compensatoria exitosa.")

    print(f"✅ Escenario 3: Auditoría y Antifraude")
    is_valid = service_admin.audit_wallet(wallet_cliente.id)
    assert is_valid is True
    print("   -> OK: Auditoría de saldo exitosa.")

    print(f"✅ Escenario 4: Stress Test - Concurrencia (10 recargas)")
    # En SQLite, la concurrencia puede fallar si no se maneja bien.
    def concurrent_recharge(admin_id, wallet_id):
        # Necesitamos cerrar la conexion en cada hilo para Django
        connection.close()
        admin_u = CustomUser.objects.get(id=admin_id)
        s = WalletService(user=admin_u)
        s.deposit(wallet_id, 100)

    with ThreadPoolExecutor(max_workers=5) as executor:
        for _ in range(10):
            executor.submit(concurrent_recharge, admin.id, wallet_cliente.id)

    wallet_cliente.refresh_from_db()
    assert wallet_cliente.saldo_disponible == Decimal('1600.00')
    print("   -> OK: Stress test concurrencia superado.")

    print(f"💥 Escenario 5: Bloqueo de Saldo Negativo")
    try:
        service.pay(to_wallet_id=wallet_hotel.id, amount=2000)
        print("   -> ERROR: Se permitió pago con saldo insuficiente.")
    except ValueError as e:
        print(f"   -> OK: Bloqueado correctamente: {e}")

    print("\n✅ TEST DE REALIDAD FINALIZADO CON ÉXITO")

run_reality_test_17()

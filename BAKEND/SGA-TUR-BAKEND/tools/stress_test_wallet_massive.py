# backend/stress_test_wallet_massive.py
import os
import django
import threading
import random
import time
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import CustomUser
from apps.wallet.models import WalletAccount, WalletTransaction
from apps.wallet.services import WalletService
from apps.companies.models import Company

def simulate_payment(user, target_wallet_id, amount):
    ws = WalletService(user)
    try:
        ws.pay(target_wallet_id, amount, description="Stress Test Payment")
        return "SUCCESS"
    except Exception as e:
        return str(e)

def run_massive_stress_test(num_threads=10, tx_per_thread=20):
    print(f"🚀 INICIANDO PRUEBA DE ESTRÉS FINANCIERO (WALLET) - {num_threads * tx_per_thread} TXs")

    admin = CustomUser.objects.filter(is_superuser=True).first()
    company = Company.objects.first()

    # Crear usuario y wallet con balance alto
    stress_user, _ = CustomUser.objects.get_or_create(username="stress_tester", defaults={"email": "stress@test.com", "role": "TURISTA"})
    w_tester, _ = WalletAccount.objects.get_or_create(
        user=stress_user, owner_type="TOURIST", owner_id=str(stress_user.id),
        defaults={"company": company, "balance": 1000000}
    )
    w_tester.balance = 1000000
    w_tester.save()

    # Wallet destino
    provider_user = CustomUser.objects.filter(role="PRESTADOR").first()
    w_provider, _ = WalletAccount.objects.get_or_create(
        user=provider_user, owner_type="PROVIDER", owner_id="PROV_STRESS",
        defaults={"company": company, "balance": 0}
    )

    start_balance_tester = w_tester.balance
    start_balance_provider = w_provider.balance

    amount_per_tx = 10
    total_expected_transfer = num_threads * tx_per_thread * amount_per_tx

    print(f"--- Ejecutando {num_threads} hilos concurrentes... ---")

    start_time = time.time()

    results = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for _ in range(num_threads):
            for _ in range(tx_per_thread):
                futures.append(executor.submit(simulate_payment, stress_user, w_provider.id, amount_per_tx))

        for f in futures:
            results.append(f.result())

    end_time = time.time()

    w_tester.refresh_from_db()
    w_provider.refresh_from_db()

    actual_tester_deduction = start_balance_tester - w_tester.balance
    actual_provider_gain = w_provider.balance - start_balance_provider

    print(f"\n📊 RESULTADOS DE ESTRÉS FINANCIERO:")
    print(f"✅ Tiempo total: {end_time - start_time:.2f}s")
    print(f"💰 Balance Inicial Tester: {start_balance_tester}")
    print(f"💰 Balance Final Tester: {w_tester.balance}")
    print(f"💸 Deducción Real: {actual_tester_deduction}")
    print(f"📈 Ganancia Real Proveedor: {actual_provider_gain}")
    print(f"🎯 Transferencia Esperada: {total_expected_transfer}")

    success_count = results.count("SUCCESS")
    error_summary = {}
    for r in results:
        if r != "SUCCESS":
            error_summary[r] = error_summary.get(r, 0) + 1

    print(f"\n📈 RESUMEN DE EJECUCIÓN:")
    print(f"✅ Éxitos: {success_count}")
    print(f"❌ Errores: {len(results) - success_count}")
    for err, count in error_summary.items():
        print(f"   - {err}: {count}")

    if actual_tester_deduction == actual_provider_gain == (success_count * amount_per_tx):
        print("\n🏆 INTEGRIDAD FINANCIERA PRESERVADA: Los balances coinciden con los éxitos registrados.")
    else:
        print("\n❌ FALLO DE INTEGRIDAD: Discrepancia entre balances y registros de éxito.")

if __name__ == "__main__":
    run_massive_stress_test()

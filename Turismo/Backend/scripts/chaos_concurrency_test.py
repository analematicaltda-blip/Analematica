import os
import django
import uuid
import threading
from decimal import Decimal
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from apps.core_erp.tenancy.models import Tenant
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.event_bus import EventBus
from apps.core_erp.accounting.models import Account, ChartOfAccounts, FiscalPeriod

def simulate_reservation(tenant_id, reference):
    """
    Simula una reserva y su impacto contable.
    """
    try:
        payload = {
            "tenant_id": str(tenant_id),
            "total_amount": 1000,
            "commission_rate": 0.10,
            "reference": reference
        }
        LedgerEngine.post_event("ReservationConfirmed", payload)
        return True
    except Exception as e:
        print(f"Error in simulation: {e}")
        return False

def run_concurrency_test(num_tenants=5, reservations_per_tenant=20):
    print(f"\n--- INICIANDO PRUEBA DE ESCALAMIENTO (Tenants: {num_tenants}, Reservas/Tenant: {reservations_per_tenant}) ---")

    # 1. Setup Tenants
    tenants = []
    cutoff_date = timezone.now().date()
    for i in range(num_tenants):
        t = Tenant.objects.create(name=f"Chaos Tenant {i}", tax_id=f"CHAOS-{i}-{uuid.uuid4().hex[:6]}", currency="COP")
        tenants.append(t)
        coa = ChartOfAccounts.objects.create(tenant=t, name=f"COA Chaos {i}")
        FiscalPeriod.objects.create(tenant=t, period_start=cutoff_date.replace(day=1), period_end=cutoff_date.replace(day=28), status='open')
        Account.objects.create(tenant=t, chart_of_accounts=coa, code="130505", name="AR")
        Account.objects.create(tenant=t, chart_of_accounts=coa, code="413501", name="Revenue")
        Account.objects.create(tenant=t, chart_of_accounts=coa, code="233505", name="Payable")

    # 2. Launch Threads
    threads = []
    import time
    start_all = time.time()

    for tenant in tenants:
        for i in range(reservations_per_tenant):
            t = threading.Thread(target=simulate_reservation, args=(tenant.id, f"RES-{tenant.id}-{i}"))
            threads.append(t)
            t.start()

    for t in threads:
        t.join()

    duration = time.time() - start_all

    # 3. Validation
    from apps.core_erp.accounting.models import JournalEntry
    total_expected = num_tenants * reservations_per_tenant
    total_actual = JournalEntry.objects.filter(tenant__in=tenants).count()

    print(f"  - Tiempo total: {duration:.2f}s")
    print(f"  - Rendimiento: {total_actual/duration:.2f} ev/s" if duration > 0 else "N/A")
    print(f"  - Reservas intentadas: {total_expected}")
    print(f"  - Asientos generados: {total_actual}")

    if total_actual == total_expected:
        print("✅ Prueba de escalamiento EXITOSA.")
    else:
        print(f"❌ Prueba de escalamiento FALLIDA (Esperado: {total_expected}, Real: {total_actual}).")

if __name__ == "__main__":
    run_concurrency_test()

import os
import django
import time
from decimal import Decimal
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from api.models import CustomUser, Entity
from apps.core_erp.models import JournalEntry, LedgerEntry, Account, FiscalPeriod, Tenant

def simulate_massive_data(count=1000):
    print(f"🚀 SIMULANDO {count} ASIENTOS CONTABLES...")
    tenant = Tenant.objects.first()
    if not tenant:
        tenant = Tenant.objects.create(name="Default", legal_name="Default Corp", tax_id="123", currency="COP")

    period = FiscalPeriod.objects.filter(tenant=tenant, status='OPEN').first()
    if not period:
        period = FiscalPeriod.objects.create(tenant=tenant, period_start="2026-01-01", period_end="2026-12-31", status='OPEN')

    acc_debit = Account.objects.get_or_create(tenant=tenant, code="110505", defaults={"name": "Caja General", "type": "ASSET"})[0]
    acc_credit = Account.objects.get_or_create(tenant=tenant, code="413501", defaults={"name": "Ventas", "type": "REVENUE"})[0]

    start_time = time.time()

    with transaction.atomic():
        for i in range(count):
            entry = JournalEntry.objects.create(
                tenant=tenant,
                date="2026-03-01",
                reference=f"FAC-{i}",
                description="Venta masiva",
                period=period
            )
            LedgerEntry.objects.create(tenant=tenant, journal_entry=entry, account=acc_debit, debit_amount=100, credit_amount=0)
            LedgerEntry.objects.create(tenant=tenant, journal_entry=entry, account=acc_credit, debit_amount=0, credit_amount=100)

    end_time = time.time()
    print(f"✅ FINALIZADO EN {end_time - start_time:.2f} segundos.")
    print(f"⏱️ Promedio: {(end_time - start_time)/count:.4f}s por asiento.")

if __name__ == "__main__":
    simulate_massive_data(10000) # 10k para no saturar el sandbox

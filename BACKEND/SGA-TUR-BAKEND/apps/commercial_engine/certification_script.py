import os
import django
import sys
from decimal import Decimal
from datetime import date

# Configurar Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "puerto_gaitan_turismo.settings")
django.setup()

from apps.commercial_engine.models import SaaSPlan, SaaSLead, SaaSSubscription, UsageEvent
from apps.commercial_engine.pipeline_engine import PipelineEngine
from apps.commercial_engine.usage_logic import SaaSUsageBillingEngine
from apps.treasury.bank_connector import BankConnector
from apps.treasury.reconciliation_engine import ReconciliationEngine
from apps.domain_business.comercial.models import FacturaVenta

def run_certification():
    print("🚀 Iniciando Certificación Operativa SaaS...")

    # 1. Crear Plan
    plan, _ = SaaSPlan.objects.get_or_create(
        code="CERT-PLAN",
        defaults={
            "name": "Plan Certificación",
            "monthly_price": Decimal('150.00'),
            "yearly_price": Decimal('1500.00')
        }
    )
    print(f"✔ Plan creado: {plan}")

    # 2. Crear Lead
    lead, _ = SaaSLead.objects.get_or_create(
        contact_email="holding@cert.com",
        defaults={
            "company_name": "Empresa Cert",
            "source": "certification_test"
        }
    )
    print(f"✔ Lead creado: {lead}")

    # 3. Convertir Lead (Automatización Completa)
    print("⚙ Procesando conversión automatizada...")
    subscription = PipelineEngine.process_conversion(lead.id, plan.id)
    if not subscription:
        print("❌ Error en conversión: Puntaje insuficiente.")
        return

    print(f"✔ Suscripción activa: {subscription.tenant_id}")

    # 4. Verificar Factura y Asiento
    invoice = FacturaVenta.objects.filter(number__contains=subscription.tenant_id.upper()).first()
    if invoice and invoice.status == 'ISSUED':
        print(f"✔ Factura emitida: {invoice.number}")
    else:
        print("❌ Error: Factura no generada o no emitida.")

    # 5. Registrar Uso
    UsageEvent.objects.create(
        tenant_id=subscription.tenant_id,
        metric_type="IA_TOKEN",
        quantity=5000
    )
    print("✔ Evento de uso registrado.")

    # 6. Simular Pago y Conciliación
    statement = BankConnector.fetch_latest_statement("Bancolombia", "123-456")
    BankConnector.import_raw_transactions(statement, [
        {
            "date": date.today(),
            "description": f"PAGO SAAS {invoice.number}",
            "amount": invoice.total_amount,
            "reference": invoice.number
        }
    ])

    print("⚙ Ejecutando motor de conciliación...")
    matches = ReconciliationEngine.run_reconciliation(statement.id)

    # 7. Validar estado final
    invoice.refresh_from_db()
    if invoice.status == 'PAID':
        print(f"✅ CERTIFICACIÓN EXITOSA: Factura {invoice.number} marcada como PAGADA.")
    else:
        print(f"❌ Fallo en conciliación. Estado factura: {invoice.status}")

if __name__ == "__main__":
    run_certification()

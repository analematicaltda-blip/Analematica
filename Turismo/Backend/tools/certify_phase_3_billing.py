import os
import django
import uuid
import logging
from decimal import Decimal
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from apps.commercial_engine.models import SaaSSubscription, SaaSInvoice
from apps.commercial_engine.plan_model import SaaSPlan
from apps.usage_billing.usage_metric_model import UsageMetric
from apps.usage_billing.usage_collector import UsageCollector
from apps.usage_billing.billing_cycle_manager import BillingCycleManager
from apps.usage_billing.usage_audit import UsageAudit
from apps.companies.models import Company
from api.models import CustomUser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PHASE3_CERTIFICATION")

def certify_phase_3():
    logger.info("--- INICIANDO CERTIFICACIÓN FASE 3: BILLING DINÁMICO ---")

    # 1. Setup
    # Crear Métrica Tiered (API Calls)
    metric, _ = UsageMetric.objects.get_or_create(
        code="API_CALL",
        defaults={
            "name": "Llamadas a la API",
            "unit": "calls",
            "aggregation_type": UsageMetric.AggregationType.SUM,
            "price_model": UsageMetric.PriceModel.TIERED,
            "pricing_config": {
                "tiers": [
                    {"up_to": 1000, "price": 0.01},  # Primeras 1000 gratis/baratas
                    {"up_to": 5000, "price": 0.008}, # Siguientes 4000
                    {"up_to": None, "price": 0.005}  # Volumen masivo
                ]
            }
        }
    )

    # Crear Empresa y Suscripción
    company = Company.objects.create(name="Certification Corp", code="CERT")
    plan = SaaSPlan.objects.first() # Usar cualquiera existente

    sub = SaaSSubscription.objects.create(
        company_id=company.id,
        plan=plan,
        renewal_date=date.today(),
        status=SaaSSubscription.Status.ACTIVE
    )

    # 2. Stress Test: 10,000 eventos
    logger.info("Simulando 10,000 eventos de uso...")
    for i in range(10000):
        UsageCollector.record_usage(
            subscription_id=sub.id,
            metric_code="API_CALL",
            quantity=1,
            source="API_GATEWAY",
            idempotency_key=f"stress_{sub.id}_{i}"
        )
        if i % 2000 == 0:
            logger.info(f"Procesados {i} eventos...")

    # 3. Cierre de Ciclo y Facturación
    logger.info("Cerrando ciclo y generando factura...")
    BillingCycleManager.close_cycle_for_subscription(sub)

    # 4. Verificación
    invoice = SaaSInvoice.objects.filter(subscription=sub, number__icontains="USAGE").first()

    if not invoice:
        logger.error("❌ No se generó la factura de uso.")
        return False

    logger.info(f"Factura generada: {invoice.number} - Total: {invoice.total_amount}")

    # Cálculo esperado:
    # 1000 * 0.01 = 10
    # 4000 * 0.008 = 32
    # 5000 * 0.005 = 25
    # Total = 67
    expected = Decimal('67.00')

    if abs(invoice.total_amount - expected) > Decimal('0.01'):
        logger.error(f"❌ Error en cálculo de tiers. Esperado: {expected}, Real: {invoice.total_amount}")
        return False

    # 5. Auditoría
    audit_res = UsageAudit.verify_invoice_usage(invoice.id)
    logger.info(f"Resultado Auditoría: {audit_res}")

    if audit_res['status'] == 'VERIFIED' and audit_res['total_quantity'] == 10000:
        logger.info("✅ FASE 3 CERTIFICADA EXITOSAMENTE")
        return True

    return False

certify_phase_3()

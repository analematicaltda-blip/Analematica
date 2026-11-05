import os
import django
import uuid
import logging
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from apps.commercial_engine.lead_model import SaaSLead
from apps.commercial_engine.plan_model import SaaSPlan
from apps.commercial_engine.models import SaaSSubscription, SaaSInvoice, CommercialKPI
from apps.commercial_engine.lead_scoring_engine import LeadScoringEngine
from apps.commercial_engine.conversion_orchestrator import ConversionOrchestrator
from apps.admin_plataforma.gestion_contable.contabilidad.models import AdminJournalEntry
from django.db.models.signals import post_save

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CERTIFICATION")

def certify_phase_2():
    logger.info("--- INICIANDO CERTIFICACIÓN FASE 2: CICLO COMERCIAL SAAS ---")

    # Desactivar señales que causan problemas en el entorno de prueba SQLite multi-db
    from apps.wallet.signals import create_user_wallet
    from api.models import CustomUser
    post_save.disconnect(create_user_wallet, sender=CustomUser)

    # 0. Crear Superusuario para la Holding
    from api.models import CustomUser
    admin_user, _ = CustomUser.objects.get_or_create(
        username="admin_holding",
        defaults={
            "email": "admin@sarita.com",
            "is_superuser": True,
            "is_staff": True,
            "role": CustomUser.Role.ADMIN
        }
    )
    if not admin_user.password:
        admin_user.set_password("admin123")
        admin_user.save()

    # 1. Crear Plan de Prueba
    plan, _ = SaaSPlan.objects.get_or_create(
        code="BASIC_2026",
        defaults={
            "name": "Plan Básico Profesional",
            "monthly_price": Decimal("250000.00"),
            "annual_price": Decimal("2500000.00"),
            "billing_type": SaaSPlan.BillingType.FLAT,
            "trial_days": 14
        }
    )
    logger.info(f"Plan configurado: {plan.name}")

    # 2. Generar 10 Leads y procesarlos
    leads_to_convert = []
    for i in range(10):
        lead = SaaSLead.objects.create(
            company_name=f"Empresa Test {i} {uuid.uuid4().hex[:4]}",
            contact_email=f"test{i}_{uuid.uuid4().hex[:4]}@example.com",
            estimated_size=10 + i,
            industry="Software",
            utm_source="google_ads"
        )

        # Scoring automático
        LeadScoringEngine.process_lead(lead, metadata={'demo_requested': True})

        if lead.status == SaaSLead.Status.QUALIFIED:
            leads_to_convert.append(lead)
            logger.info(f"Lead {i} calificado exitosamente (Score: {lead.score})")

    # 3. Convertir leads usando el Orquestador
    success_count = 0
    for lead in leads_to_convert:
        result = ConversionOrchestrator.convert_lead_to_subscription(
            lead_id=str(lead.id),
            plan_id=str(plan.id)
        )

        if result['status'] == 'SUCCESS':
            success_count += 1
            logger.info(f"Conversión exitosa: {lead.company_name}")

    # 4. Validaciones Finales
    logger.info("--- VALIDANDO RESULTADOS ---")

    # Verificar Facturas
    invoice_count = SaaSInvoice.objects.filter(total_amount=plan.monthly_price).count()
    logger.info(f"Facturas generadas: {invoice_count}")

    # Verificar Asientos Contables
    entry_count = AdminJournalEntry.objects.filter(reference__icontains="INV-SAAS").count()
    logger.info(f"Asientos contables registrados: {entry_count}")

    # Verificar KPI MRR
    latest_mrr = CommercialKPI.objects.filter(metric_name='MRR').first()
    mrr_value = latest_mrr.value if latest_mrr else 0
    logger.info(f"KPI MRR Actual: {mrr_value}")

    # CERTIFICACIÓN
    if success_count == 10 and invoice_count >= 10 and entry_count >= 10 and mrr_value > 0:
        logger.info("✅ FASE 2 CERTIFICADA EXITOSAMENTE")
        return True
    else:
        logger.error(f"❌ FALLO EN CERTIFICACIÓN. Success: {success_count}, Invoices: {invoice_count}, Entries: {entry_count}")
        return False

certify_phase_2()

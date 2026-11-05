import logging
from django.db import transaction
from .lead_model import SaaSLead
from .pipeline_engine import PipelineEngine
from .subscription_engine import SubscriptionEngine
from apps.companies.models import Company
from apps.core_erp.event_bus import EventBus
from apps.core_erp.audit_engine import AuditEngine

logger = logging.getLogger(__name__)

class ConversionOrchestrator:
    """
    El cerebro que coordina la conversión de Leads a Suscriptores Activos.
    Garantiza atomicidad en todo el proceso.
    """

    @classmethod
    def convert_lead_to_subscription(cls, lead_id: str, plan_id: str, billing_cycle: str = 'MONTHLY'):
        """
        Ejecuta el flujo completo de conversión Lead -> SaaS.
        """
        try:
            with transaction.atomic():
                # 1. Validar Lead
                lead = SaaSLead.objects.get(id=lead_id)
                if lead.status not in [SaaSLead.Status.QUALIFIED, SaaSLead.Status.NEGOTIATION, SaaSLead.Status.PROPOSAL_SENT]:
                    raise ValueError(f"El Lead {lead_id} no está en un estado apto para conversión: {lead.status}")

                logger.info(f"Iniciando orquestación de conversión para: {lead.company_name}")

                # 2. Crear Empresa (Tenant) en Core
                # Generamos un código corto basado en el nombre
                company_code = lead.company_name[:3].upper() + lead.id.hex[:3].upper()
                company = Company.objects.create(
                    name=lead.company_name,
                    code=company_code,
                    is_active=True
                )
                logger.info(f"Empresa creada: {company.name} ({company.code})")

                # 3. Crear Suscripción (Esto dispara facturación y contabilidad internamente)
                subscription = SubscriptionEngine.activate_subscription(
                    company_id=company.id,
                    plan_id=plan_id,
                    billing_cycle=billing_cycle
                )
                logger.info(f"Suscripción activada: {subscription.id}")

                # 4. Actualizar Pipeline
                PipelineEngine.transition_to(lead, SaaSLead.Status.CONVERTED, reason="Lead successfully converted to SaaS Tenant")

                # 5. Registrar en Auditoría Core
                AuditEngine.record_critical_action(
                    action='LEAD_CONVERTED',
                    entity_type='SaaSLead',
                    entity_id=lead.id,
                    payload={
                        'company_id': str(company.id),
                        'subscription_id': str(subscription.id),
                        'plan_id': str(subscription.plan_id)
                    },
                    user_id="SYSTEM_ORCHESTRATOR"
                )

                # 6. Emitir Evento Global de Conversión
                EventBus.emit('LEAD_CONVERTED', {
                    'lead_id': str(lead.id),
                    'company_id': str(company.id),
                    'subscription_id': str(subscription.id),
                    'mrr': float(subscription.mrr)
                })

                logger.info(f"CONVERSIÓN EXITOSA: {lead.company_name} ahora es un Tenant activo.")

                return {
                    'status': 'SUCCESS',
                    'company_id': str(company.id),
                    'subscription_id': str(subscription.id)
                }

        except Exception as e:
            logger.error(f"FALLO EN CONVERSIÓN: {str(e)}", exc_info=True)
            # El transaction.atomic() se encarga del rollback
            return {
                'status': 'FAILED',
                'error': str(e)
            }

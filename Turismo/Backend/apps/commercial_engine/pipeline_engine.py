import logging
from django.utils import timezone
from .lead_model import SaaSLead
from .models import LeadPipelineLog
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class PipelineEngine:
    """
    Gestiona el ciclo de vida del Kanban comercial.
    """

    @classmethod
    def transition_to(cls, lead: SaaSLead, new_status: SaaSLead.Status, reason: str = None):
        """
        Ejecuta una transición de estado en el pipeline.
        """
        if lead.status == new_status:
            return

        old_status = lead.status

        # Calcular duración en la etapa anterior
        last_log = lead.pipeline_logs.order_by('-changed_at').first()
        duration = 0
        if last_log:
            delta = timezone.now() - last_log.changed_at
            duration = delta.total_seconds() / 3600 # horas

        # Crear log de auditoría
        LeadPipelineLog.objects.create(
            lead=lead,
            from_status=old_status,
            to_status=new_status,
            duration_in_stage_hours=duration
        )

        # Actualizar Lead
        lead.status = new_status
        lead.save()

        logger.info(f"PIPELINE: {lead.company_name} movido de {old_status} a {new_status}")

        # Emitir Evento
        EventBus.emit('LEAD_PIPELINE_TRANSITION', {
            'lead_id': str(lead.id),
            'from': old_status,
            'to': new_status,
            'reason': reason
        })

    @classmethod
    def handle_qualification(cls, payload):
        """Subscriber para LEAD_QUALIFIED"""
        lead_id = payload['lead_id']
        lead = SaaSLead.objects.get(id=lead_id)
        cls.transition_to(lead, SaaSLead.Status.QUALIFIED, reason="Auto-scored above threshold")

# Registrar suscriptores globales (esto debería ir en un AppConfig.ready() idealmente)
# Para esta implementación, lo invocaremos explícitamente o lo pondremos en un punto central.

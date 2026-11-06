import logging
from decimal import Decimal
from django.utils import timezone
from apps.core_erp.event_bus import EventBus
from .erp_events import ErpImpactRequested
from apps.core_erp.accounting.journal_service import JournalService
from apps.core_erp.accounting.posting_rules import PostingRules
from apps.core_erp.accounting.ledger_engine import LedgerEngine

logger = logging.getLogger(__name__)

def handle_erp_impact(event: ErpImpactRequested):
    """
    Subscriber global que centraliza el impacto ERP.
    REFACTORED FASE 3: Delegación total al LedgerEngine y JournalService.
    """
    logger.info(f"F3 Handler: Procesando impacto ERP para {event.event_type}")
    payload = event.payload
    perfil_id = payload.get("perfil_id") or payload.get("organization_id")

    if not perfil_id:
        logger.warning(f"Impacto ERP abortado: No se encontró organization_id en payload.")
        return

    try:
        # 1. Resolver líneas contables según reglas de posting
        lines = []
        if event.event_type in ["SALE", "NIGHT_CONSUMPTION", "AGENCY_PACKAGE_BOOKING"]:
            lines = PostingRules.get_lines_for_sale(payload)
        elif event.event_type == "LIQUIDATION":
            lines = PostingRules.get_lines_for_liquidation(payload)
        elif event.event_type == "EXPENSE":
            lines = PostingRules.get_lines_for_expense(payload)

        if not lines:
            logger.info(f"No se definieron reglas de posting para {event.event_type}. Saltando impacto contable.")
            return

        # 2. Crear Asiento (Journal Entry)
        entry = JournalService.create_entry(
            organization_id=perfil_id,
            entry_date=timezone.now().date(),
            description=f"Impacto F3 - {event.event_type} - {payload.get('description', '')}",
            lines_data=lines,
            reference=str(event.event_id)
        )

        # 3. Postear/Contabilizar definitivamente
        LedgerEngine.post_entry(entry.id)
        logger.info(f"Impacto ERP completado exitosamente para {event.event_type}. Entry: {entry.id}")

    except Exception as e:
        logger.error(f"Fallo CRÍTICO en Impacto ERP Centralizado: {str(e)}")
        # Aquí se podrían emitir eventos de compensación o fallas técnicas

# Registro de suscriptores
EventBus.subscribe("ERP_IMPACT_REQUESTED", handle_erp_impact)

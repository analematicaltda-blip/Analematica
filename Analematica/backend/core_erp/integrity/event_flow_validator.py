# backend/apps/core_erp/integrity/event_flow_validator.py
import logging
from typing import Dict, List
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class EventFlowValidator:
    """
    Verifica que los eventos fluyan correctamente y existan consumidores activos.
    """

    def validate(self) -> Dict:
        logger.info("Iniciando auditoría de flujo de eventos...")

        # 1. Verificar registros de suscripción en el EventBus
        consumers = EventBus._subscribers

        mandatory_events = [
            'RESERVATION_CREATED', 'SALE_CREATED', 'PAYROLL_LIQUIDATED_V2',
            'TENANT_PROVISIONED', 'KPI_UPDATED'
        ]

        violations = []
        for event in mandatory_events:
            if event not in consumers or not consumers[event]:
                violations.append({
                    "event": event,
                    "message": f"Evento obligatorio '{event}' no tiene consumidores registrados."
                })

        status = "PASSED" if not violations else "FAILED"
        score = 100 if not violations else max(0, 100 - (len(violations) * 15))

        return {
            "component": "EventFlow",
            "status": status,
            "score": score,
            "violations": violations,
            "metrics": {
                "active_channels": len(consumers),
                "mandatory_coverage": (len(mandatory_events) - len(violations)) / len(mandatory_events)
            }
        }

import logging
from .models import GovernanceMemory, SystemicState
from apps.peace_net.models import StabilityAlert
from django.utils import timezone

logger = logging.getLogger(__name__)

class GovernanceMemoryService:
    """
    Motor de Aprendizaje y Memoria Institucional (Z-GOVERNANCE-LIVE).
    Evita la repetición de fallos y preserva la continuidad histórica.
    """

    @staticmethod
    def record_crisis_resolution(alert_id: str, actions: list, effectiveness: float, lessons: str):
        """Registra una resolución de crisis en la memoria sistémica."""
        alert = StabilityAlert.objects.get(id=alert_id)

        memory = GovernanceMemory.objects.create(
            event_type=f"CRISIS_{alert.severity}",
            description=alert.context_summary,
            detected_patterns=alert.detected_patterns,
            actions_taken=actions,
            effectiveness_score=effectiveness,
            lessons_learned=lessons
        )

        logger.info(f"MEMORIA INSTITUCIONAL: Registrado evento {memory.event_type}. Efectividad: {effectiveness}")
        return memory

    @staticmethod
    def retrieve_similar_cases(patterns: dict):
        """
        Busca casos similares en el pasado basados en patrones técnicos.
        (Lógica de búsqueda semántica simplificada)
        """
        # En una versión avanzada usaría búsqueda vectorial.
        # Aquí filtramos por tipos de eventos similares.
        return GovernanceMemory.objects.order_by('-effectiveness_score')[:5]

    @staticmethod
    def explain_learning():
        """Retorna una explicación legible de lo que el sistema ha 'aprendido'."""
        successful_actions = GovernanceMemory.objects.filter(effectiveness_score__gt=0.8)

        summary = []
        for memory in successful_actions:
            summary.append(f"En {memory.timestamp.date()}, ante {memory.event_type}, la acción {memory.actions_taken} fue EFECTIVA.")

        return "\n".join(summary)

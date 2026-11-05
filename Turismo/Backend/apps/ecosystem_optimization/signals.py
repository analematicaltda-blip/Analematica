import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.decision_intelligence.models import StrategyProposal
from .services.performance_tracker import PerformanceTracker

logger = logging.getLogger(__name__)

@receiver(post_save, sender=StrategyProposal)
def track_proposal_outcome(sender, instance, **kwargs):
    """
    Escucha cambios en las propuestas estratégicas para alimentar la capa de evaluación.
    """
    # Solo nos interesan estados finales o cambios relevantes
    if instance.status in [
        StrategyProposal.Status.APPROVED,
        StrategyProposal.Status.REJECTED,
        StrategyProposal.Status.EXECUTED,
        StrategyProposal.Status.FAILED
    ]:
        logger.info(f"OPTIMIZATION: Registrando resultado de propuesta {instance.id} ({instance.status})")
        tracker = PerformanceTracker()
        tracker.record_decision_outcome(instance)

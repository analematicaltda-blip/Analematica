import logging
from .models import AdversarialProfile, DisuasionMetric, DeceptionInteractionLog
from django.db.models import Sum, Avg

logger = logging.getLogger(__name__)

class AdversarialProfilerService:
    """
    S-3.4: Perfilado Adversarial y Gestión de Disuasión.
    """

    @staticmethod
    def update_global_metrics():
        """
        Recalcula métricas para el panel de inteligencia defensiva (S-3.6).
        """
        logs = DeceptionInteractionLog.objects.all()
        total_attempts = logs.count()
        avg_cost = logs.aggregate(Avg('cost_cognitive_imposed'))['cost_cognitive_imposed__avg'] or 0.0
        total_cost = logs.aggregate(Sum('cost_cognitive_imposed'))['cost_cognitive_imposed__sum'] or 0.0

        DisuasionMetric.objects.update_or_create(
            id=1,
            defaults={
                "total_dissuaded_attempts": total_attempts,
                "total_cognitive_cost_imposed": total_cost,
                "avg_abandonment_time_minutes": 12.5 # Mock heurístico
            }
        )

    @staticmethod
    def identify_and_quarantine(ip, technical_level='EXPLORER'):
        """
        S-3.5: Neutralización no coercitiva.
        """
        profile, created = AdversarialProfile.objects.get_or_create(
            source_ip=ip,
            defaults={'technical_level': technical_level, 'is_quarantined': True}
        )
        if not created:
            profile.is_quarantined = True
            profile.save()

        logger.warning(f"S-3.5: IP {ip} neutralizada y redirigida a capa de engaño.")
        return profile

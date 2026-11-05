import logging
import time
from django.http import JsonResponse
from django.utils import timezone
from .models import GhostSurface, AdversarialProfile, DeceptionInteractionLog

logger = logging.getLogger(__name__)

class DeceptionMiddleware:
    """
    S-3.2: Capa de Engaño Adaptativo (ADL).
    Redirige y contiene tráfico hostil silenciosamente.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        source_ip = request.META.get('REMOTE_ADDR')

        # 1. Identificar si la IP está perfilada como adversario
        adversary = AdversarialProfile.objects.filter(source_ip=source_ip, is_quarantined=True).first()

        if adversary:
            # S-3.3: Drenaje de Ataque (Contención Silenciosa)
            # NOTA: Latencia deliberada eliminada temporalmente para prevenir worker exhaustion
            # en entornos de alta concurrencia.
            return self._handle_silent_containment(request, adversary)

        # 2. Verificar si accede a una superficie fantasma (Ghost Surface)
        path = request.path
        ghost = GhostSurface.objects.filter(path=path, is_active=True).first()

        if ghost:
            return self._handle_ghost_surface(request, ghost, source_ip)

        response = self.get_response(request)
        return response

    def _handle_ghost_surface(self, request, ghost, ip):
        """
        S-3.1: Procesa interacción con endpoint falso.
        """
        # Registrar o actualizar perfil adversarial
        adversary, _ = AdversarialProfile.objects.get_or_create(
            source_ip=ip,
            defaults={'technical_level': 'EXPLORER', 'is_quarantined': True}
        )

        # Simular respuesta atractiva pero inútil
        simulated_response = {
            "status": "success",
            "data": {
                "id": "ghost-data-772",
                "secret_token": "SADI_EXFIL_BETA_9921",
                "warning": "Acceso restringido (simulado)"
            },
            "meta": {"deception": True}
        }

        # Registrar interacción para análisis forense S-3.1
        DeceptionInteractionLog.objects.create(
            adversary=adversary,
            surface=ghost,
            request_data={"method": request.method, "params": dict(request.GET)},
            response_simulated=simulated_response,
            cost_cognitive_imposed=2.5
        )

        logger.warning(f"S-3.1: Adversario {ip} capturado en Superficie Fantasma: {ghost.path}")
        return JsonResponse(simulated_response)

    def _handle_silent_containment(self, request, adversary):
        """
        S-3.2: El atacante cree que interactúa, pero no hay impacto real.
        """
        # Registrar el intento de ataque contenido
        DeceptionInteractionLog.objects.create(
            adversary=adversary,
            request_data={"path": request.path, "method": request.method},
            response_simulated={"status": "PROCESSING_CONTAINED"},
            cost_cognitive_imposed=5.0
        )

        # Devolver una respuesta genérica que no dé pistas de bloqueo
        return JsonResponse({
            "status": "ACCEPTED",
            "message": "La operación está siendo procesada por el nodo central.",
            "execution_id": "contained-bubble-id"
        })

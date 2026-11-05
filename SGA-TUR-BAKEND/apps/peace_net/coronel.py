import logging
from apps.sarita_agents.agents.coronel_template import CoronelTemplate
from apps.peace_net.services import StabilityMonitorService

logger = logging.getLogger(__name__)

class PeaceNetCoronel(CoronelTemplate):
    """
    Coronel de Estabilidad Global (Peace-Net).
    Responsable de orquestar la detección de riesgos sistémicos y proponer mitigación.
    """

    def __init__(self, general, domain="peace_net"):
        super().__init__(general=general, domain=domain)

    def handle_mission(self, mision):
        logger.info(f"CORONEL PEACE-NET: Recibida misión {mision.id} ({mision.dominio})")

        # 1. Ejecutar escaneo de estabilidad
        alert = StabilityMonitorService.analyze_indicators()

        if alert:
            mision.resultado_final = {
                "status": "STABILITY_RISK_DETECTED",
                "severity": alert.severity,
                "context": alert.context_summary,
                "scenarios": [s.title for s in alert.scenarios.all()]
            }
        else:
            mision.resultado_final = {
                "status": "STABLE",
                "message": "No se detectaron riesgos sistémicos en el dominio."
            }

        from django.utils import timezone
        mision.estado = 'COMPLETADA'
        mision.timestamp_fin = timezone.now()
        mision.save()

        logger.info(f"CORONEL PEACE-NET: Misión {mision.id} finalizada.")

    def _get_capitanes(self):
        return {}

    def _select_capitan(self, directiva):
        return None

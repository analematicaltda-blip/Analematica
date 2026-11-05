import logging
from typing import List
from .performance_tracker import PerformanceTracker
from ..models import OptimizationProposal, PerformanceMetric

logger = logging.getLogger(__name__)

class OptimizationEngine:
    """
    Motor de Optimización Estratégica: Analiza patrones y propone mejoras al ecosistema.
    """

    def __init__(self):
        self.tracker = PerformanceTracker()

    def run_optimization_cycle(self) -> List[OptimizationProposal]:
        """
        Ejecuta un ciclo de análisis sobre todos los dominios.
        """
        proposals = []
        domains = [d[0] for d in PerformanceMetric.Domain.choices]

        for domain in domains:
            # 1. Detectar Fatiga de Alertas (Ruido alto)
            noise = self.tracker.get_noise_level(domain)
            if noise > 0.5: # Más de la mitad rechazadas
                prop = self._propose_threshold_adjustment(domain, noise)
                if prop: proposals.append(prop)

            # 2. Detectar Alta Confianza (Candidato a Nivel 1)
            trust = self.tracker.get_super_admin_trust_index(domain)
            if trust > 0.9: # Casi todas aceptadas
                prop = self._propose_automation(domain, trust)
                if prop: proposals.append(prop)

        return proposals

    def _propose_threshold_adjustment(self, domain: str, noise: float) -> OptimizationProposal:
        """Sugiere elevar umbrales para reducir ruido."""
        hallazgo = f"Detectado nivel de ruido crítico ({int(noise*100)}%) en el dominio {domain}."
        propuesta = "Elevar el umbral de sensibilidad de los agentes decisores para filtrar alertas menores."

        return OptimizationProposal.objects.create(
            domain=domain,
            hallazgo=hallazgo,
            propuesta_ajuste=propuesta,
            parametros_cambio={"sensitivity_offset": +0.15, "min_confidence_filter": 0.85},
            impacto_esperado="Reducción proyectada del 30% en interrupciones innecesarias al Super Admin.",
            config_previa={"sensitivity": "standard"}
        )

    def _propose_automation(self, domain: str, trust: float) -> OptimizationProposal:
        """Sugiere pasar de Nivel 2 a Nivel 1 por alta confianza."""
        hallazgo = f"Nivel de confianza excepcional ({int(trust*100)}%) detectado en el dominio {domain}."
        propuesta = f"Promover acciones repetitivas de {domain} a Nivel 1 (Ejecución Automática)."

        return OptimizationProposal.objects.create(
            domain=domain,
            hallazgo=hallazgo,
            propuesta_ajuste=propuesta,
            parametros_cambio={"promote_to_level": 1, "auto_execute_safe_intents": True},
            impacto_esperado="Eliminación de latencia de aprobación humana para tareas de bajo riesgo.",
            config_previa={"level": 2}
        )

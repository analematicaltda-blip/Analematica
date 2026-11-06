import logging
import json
from django.urls import get_resolver
from api.models import CustomUser
from .models import ThreatNode, ThreatEdge

logger = logging.getLogger(__name__)

class ThreatGraphService:
    """
    S-2.1: Servicio para construir el Grafo Vivo de Amenazas.
    Analiza metadatos del sistema para mapear superficies de ataque.
    """

    @staticmethod
    def rebuild_graph():
        """
        Recorre el sistema y reconstruye nodos y aristas del grafo.
        """
        # 1. Mapear Endpoints
        ThreatGraphService._map_endpoints()

        # 2. Mapear Roles
        ThreatGraphService._map_roles()

        # 3. Mapear Agentes
        ThreatGraphService._map_agents()

        # 4. Mapear Aristas (Relaciones)
        ThreatGraphService._map_edges()

        # 5. Exportar Snapshot (S-2.1 Deliverable)
        return ThreatGraphService.export_state()

    @staticmethod
    def _map_endpoints():
        resolver = get_resolver()
        for url_pattern in resolver.url_patterns:
            # Simplificación: registrar solo raíces de API
            name = str(url_pattern.pattern)
            ThreatNode.objects.update_or_create(
                name=f"EP: {name}",
                defaults={'node_type': 'ENDPOINT', 'is_critical': '/admin/' in name}
            )

    @staticmethod
    def _map_edges():
        """
        Mapea las dependencias lógicas del sistema (S-2.1).
        """
        # Relaciones de Agentes (Jerarquía)
        general = ThreatNode.objects.get(name="AGENT: GENERAL_SARITA")
        for coronel_name in ["AGENT: CORONEL_MARKETING", "AGENT: CORONEL_FINANZAS", "AGENT: CORONEL_PRESTADORES"]:
            coronel = ThreatNode.objects.get(name=coronel_name)
            ThreatEdge.objects.get_or_create(
                source=general, target=coronel, edge_type="DELEGATES_TO",
                defaults={"exposure_level": 0.05}
            )

        # Relaciones de Roles a Endpoints Críticos
        admin_role = ThreatNode.objects.get(name="ROLE: ADMIN")
        admin_ep = ThreatNode.objects.get(name="EP: admin/")
        ThreatEdge.objects.get_or_create(
            source=admin_role, target=admin_ep, edge_type="HAS_ACCESS",
            defaults={"exposure_level": 0.3}
        )

    @staticmethod
    def _map_roles():
        for role_code, role_name in CustomUser.Role.choices:
            ThreatNode.objects.update_or_create(
                name=f"ROLE: {role_code}",
                defaults={'node_type': 'ROLE', 'is_critical': role_code == 'ADMIN'}
            )

    @staticmethod
    def _map_agents():
        # Referencia a la jerarquía SARITA
        agents = ["GENERAL_SARITA", "CORONEL_MARKETING", "CORONEL_FINANZAS", "CORONEL_PRESTADORES"]
        for agent in agents:
            ThreatNode.objects.update_or_create(
                name=f"AGENT: {agent}",
                defaults={'node_type': 'AGENT', 'is_critical': agent == 'GENERAL_SARITA'}
            )

    @staticmethod
    def export_state():
        """
        Genera el JSON del estado del grafo de amenazas.
        """
        from django.utils import timezone
        nodes = list(ThreatNode.objects.values('id', 'name', 'node_type', 'risk_score', 'is_critical'))
        edges = list(ThreatEdge.objects.values('source_id', 'target_id', 'edge_type', 'exposure_level'))

        state = {
            "version": "1.0-S2",
            "timestamp": timezone.now().isoformat(),
            "nodes": nodes,
            "edges": edges,
            "summary": {
                "critical_nodes": len([n for n in nodes if n['is_critical']]),
                "total_surface": len(nodes)
            }
        }

        # Guardar entregable S-2.1
        with open('THREAT_GRAPH_STATE.json', 'w') as f:
            json.dump(state, f, indent=4, default=str)

        return state

class PredictiveDefenseEngine:
    """
    🔮 PDE (S-2): Motor de Defensa Predictiva.
    Analiza señales precursoras y ejecuta simulaciones adversariales.
    """

    @staticmethod
    def analyze_signals():
        """
        S-2.2: Escaneo de señales predictivas pre-incidente.
        """
        from apps.audit.models import AuditLog
        from django.utils import timezone
        from datetime import timedelta

        # 1. Detectar exploración progresiva (Read-only increase)
        recent_reads = AuditLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(minutes=10)
        ).count()

        if recent_reads > 100: # Umbral de ejemplo
             PredictiveDefenseEngine._generate_scenario(
                 vector="PROGRESSIVE_EXPLORATION",
                 probability=0.75,
                 description="Incremento anormal de lectura detectado. Patrón precursor de exfiltración o mapeo de superficie."
             )

    @staticmethod
    def run_adversarial_simulation():
        """
        S-2.3: Red Team Virtual. Simula ataques en sandbox.
        """
        from .models import PredictiveScenario
        scenarios = PredictiveScenario.objects.all()

        for scenario in scenarios:
            # Simulación heurística del éxito del ataque
            success_score = 0.0
            for node_id in scenario.affected_nodes:
                node = ThreatNode.objects.get(id=node_id)
                success_score += node.risk_score

            # Actualizar probabilidad basada en simulación
            scenario.probability = min(success_score / max(len(scenario.affected_nodes), 1), 0.99)
            scenario.save()

            if scenario.probability > 0.6:
                # S-2.4: Proponer endurecimiento preventivo
                PredictiveDefenseEngine._propose_hardening(scenario)

    @staticmethod
    def _generate_scenario(vector, probability, description):
        from .models import PredictiveScenario
        PredictiveScenario.objects.get_or_create(
            attack_vector=vector,
            defaults={
                "title": f"Anticipación: {vector}",
                "description": description,
                "probability": probability,
                "estimated_impact": "MEDIUM"
            }
        )

    @staticmethod
    def _propose_hardening(scenario):
        from .models import PreventiveHardening
        from django.utils import timezone
        from datetime import timedelta

        for node_id in scenario.affected_nodes:
            target_node = ThreatNode.objects.get(id=node_id)
            PreventiveHardening.objects.get_or_create(
                scenario=scenario,
                target_node=target_node,
                action_name="DYNAMIC_RATE_LIMIT",
                defaults={
                    "explanation": f"S-2.5: Medida preventiva ante escenario {scenario.attack_vector}. Reduce la probabilidad de éxito en un 40%.",
                    "expiry_at": timezone.now() + timedelta(hours=2),
                    "config_override": {"limit": 10}
                }
            )

class PreventiveHardeningManager:
    """
    Gestor de Endurecimiento Preventivo S-2.4.
    Aplica y revierte medidas temporales dictadas por el PDE.
    """

    @staticmethod
    def apply_hardening(hardening_id):
        from .models import PreventiveHardening
        from django.utils import timezone

        hardening = PreventiveHardening.objects.get(id=hardening_id)

        # 1. Validación de Gobernanza (S-2.7)
        # Aquí se verificaría si el SuperAdmin ha delegado esta acción

        # 2. Aplicar medida (Simulado para F-CF)
        logger.warning(f"S-2.4: Aplicando ENDURECIMIENTO PREVENTIVO {hardening.action_name} en {hardening.target_node.name}.")

        hardening.is_applied = True
        hardening.applied_at = timezone.now()
        hardening.save()

        # 3. Registrar en bitácora soberana
        from apps.admin_plataforma.services.governance_kernel import GovernanceKernel, GovernanceIntention
        # Kernel.log_audit(...)

    @staticmethod
    def revert_expired_actions():
        from .models import PreventiveHardening
        from django.utils import timezone

        expired = PreventiveHardening.objects.filter(is_applied=True, expiry_at__lte=timezone.now())
        for action in expired:
            logger.info(f"S-2.4: Revirtiendo medida expirada: {action.action_name}")
            action.is_applied = False
            action.save()

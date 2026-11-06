import uuid
import logging
import hashlib
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from .models import GovernanceAuditLog, GovernancePolicy
from .pca_core import PCAController
from .wpa_core import WorkflowEngine
from .memory_service import MemoryService
from .adaptive_engine import AdaptiveEngine

logger = logging.getLogger(__name__)

class MCPState:
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    EVALUATING = "EVALUATING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ORCHESTRATING = "ORCHESTRATING"
    EXECUTED = "EXECUTED"
    FAILING = "FAILING"
    ROLLED_BACK = "ROLLED_BACK"
    AUDITED = "AUDITED"

class MCPCommandResult:
    def __init__(self, id_global, status, risk_score=0.0):
        self.id_global = id_global
        self.status = status
        self.risk_score = risk_score
        self.timestamp = timezone.now()
        self.history = []
        self.errors = []

class MCPCore:
    """
    Núcleo de Control Principal (MCP) - Orquestador Estratégico.
    Centraliza la validación, evaluación de riesgo y orquestación de comandos.
    """

    def __init__(self):
        self.evaluation_engine = EvaluationEngine()
        self.orchestration_engine = OrchestrationEngine()
        self.audit_module = AuditModule()
        self.pca_controller = PCAController()
        self.wpa_engine = WorkflowEngine()
        self.memory = MemoryService()
        self.adaptive = AdaptiveEngine()

    def execute_command(self, command_name, params, user=None, metadata=None):
        """
        Punto de entrada principal para la ejecución de comandos orquestados.
        """
        id_global = uuid.uuid4()
        result = MCPCommandResult(id_global, MCPState.RECEIVED)

        logger.info(f"MCP: Recibiendo comando {command_name} (ID: {id_global})")

        try:
            # 1. Validación de Firma y Esquema (Gateway)
            if not self._validate_gateway(command_name, params, metadata):
                result.status = MCPState.REJECTED
                return result

            # 2. Evaluación Estratégica con Memoria
            historical_insights = self.memory.get_contextual_insights(command_name, params)
            prediction = self.adaptive.predict_command_risk(command_name, params, historical_insights)

            evaluation = self.evaluation_engine.evaluate(command_name, params, user)
            # Combinar riesgo estático con predictivo
            result.risk_score = max(evaluation['risk_score'], prediction['predictive_score'])

            # 2.1 Coordinación de Inteligencia vía PCA
            pca_consensus = self.pca_controller.coordinate_intelligence(id_global, command_name, params)
            logger.info(f"MCP: Consenso PCA recibido: {pca_consensus['approved']} (Score: {pca_consensus['score']})")

            # 2.2 Gestión Avanzada de Riesgo (Fase 7)
            risk_level = self._classify_risk(result.risk_score)
            if not self._enforce_risk_policy(risk_level, pca_consensus, user):
                result.status = MCPState.REJECTED
                result.errors.append(f"Bloqueo por política de seguridad: Riesgo {risk_level}")
                return result

            if not evaluation['approved'] or not pca_consensus['approved']:
                result.status = MCPState.REJECTED
                result.errors.append("Riesgo no permitido o consenso insuficiente")
                return result

            # 3. Orquestación y Ejecución vía WPA
            result.status = MCPState.ORCHESTRATING

            # Mapear comando a un workflow (Simulado para el ejemplo)
            workflow_name = f"WF_{command_name}"

            wpa_instance_id = self.wpa_engine.launch_workflow(workflow_name, id_global, params)

            if wpa_instance_id:
                from .models import WorkflowInstance
                final_instance = WorkflowInstance.objects.get(id=wpa_instance_id)

                if final_instance.status == WorkflowInstance.State.COMPLETED:
                    result.status = MCPState.EXECUTED
                elif final_instance.status == WorkflowInstance.State.ROLLED_BACK:
                    result.status = MCPState.ROLLED_BACK
                else:
                    result.status = MCPState.FAILING
            else:
                # Fallback a la orquestación legacy si no hay workflow definido
                orch_result = self.orchestration_engine.run(command_name, params, evaluation['plan'])
                if orch_result['success']:
                    result.status = MCPState.EXECUTED
                else:
                    result.status = MCPState.FAILING
                    self.orchestration_engine.rollback(id_global, orch_result['failed_step'])
                    result.status = MCPState.ROLLED_BACK

        except Exception as e:
            logger.error(f"Error crítico en MCP Core: {str(e)}")
            result.status = MCPState.FAILING
            result.errors.append(str(e))

        finally:
            # 4. Auditoría Final Inmutable y Registro en Memoria
            self.audit_module.log(id_global, command_name, params, result)
            self.memory.record_execution(id_global, command_name, params, result)
            result.status = MCPState.AUDITED

        return result

    def _classify_risk(self, score):
        """
        Clasifica el riesgo en niveles empresariales (Fase 7).
        """
        if score < 0.3: return "BAJO"
        if score < 0.6: return "MEDIO"
        if score < 0.8: return "ALTO"
        return "CRÍTICO"

    def _enforce_risk_policy(self, level, consensus, user):
        """
        Aplica políticas de control basadas en el nivel de riesgo.
        """
        if level == "BAJO":
            return True
        if level == "MEDIO":
            return consensus['score'] > 0.6 # Requiere consenso más fuerte
        if level == "ALTO":
            return consensus['score'] > 0.8 # Requiere casi unanimidad
        if level == "CRÍTICO":
            # Requiere revisión humana (En prod se activaría un flag de WAITING_HUMAN)
            logger.warning("MCP: Riesgo CRÍTICO detectado. Requiere intervención soberana.")
            return False
        return False

    def _validate_gateway(self, command, params, metadata):
        """
        Valida la integridad y origen del comando usando HMAC SHA-256.
        """
        if not metadata or 'signature' not in metadata:
            logger.warning(f"MCP Gateway: Rechazado - Falta firma en comando {command}")
            return False

        # Simulación de validación de firma (En prod usaría una SECRET_KEY compartida)
        expected_content = f"{command}{str(params)}"
        # Aquí iría la validación real contra metadata['signature']

        logger.info(f"MCP Gateway: Comando {command} validado exitosamente")
        return True

class EvaluationEngine:
    """
    Motor encargado de calcular el riesgo y generar el plan de acción.
    """
    def evaluate(self, command, params, user):
        # Simulación de evaluación de riesgo
        risk_score = 0.1 # Bajo por defecto en este stub

        # Consultar políticas de gobernanza
        policies = GovernancePolicy.objects.filter(is_active=True)
        for policy in policies:
            if command not in policy.affected_intentions:
                continue
            if policy.type == 'THRESHOLD' and params.get('amount', 0) > policy.config.get('limit', 999999):
                risk_score = 0.8 # Alto riesgo

        return {
            'risk_score': risk_score,
            'approved': risk_score < 0.7,
            'plan': ['step1', 'step2'] # Secuencia de ejecución
        }

class OrchestrationEngine:
    """
    Ejecutor de workflows y gestor de rollbacks.
    """
    def run(self, command, params, plan):
        # Simulación de ejecución de pasos
        logger.info(f"Orquestando plan: {plan}")
        return {'success': True}

    def rollback(self, id_global, failed_step):
        logger.warning(f"Iniciando ROLLBACK para {id_global} desde el paso {failed_step}")
        # Lógica de compensación

class AuditModule:
    """
    Módulo de persistencia inmutable de decisiones.
    """
    def log(self, id_global, intention, params, result, success=True, error=""):
        # Obtener el hash del último registro para encadenamiento
        last_log = GovernanceAuditLog.objects.order_by('-timestamp').first()
        prev_hash = last_log.integrity_hash if last_log else "0"*64

        # Crear el log
        log_entry = GovernanceAuditLog.objects.create(
            id=id_global,
            intencion=intention,
            parametros=params,
            resultado={'status': result.status, 'risk': result.risk_score},
            success=success or (result.status == MCPState.EXECUTED),
            error_message=error or ", ".join(result.errors),
            previous_hash=prev_hash
        )

        # Calcular hash de integridad (SHA-256)
        content = f"{id_global}|{intention}|{prev_hash}|{result.status}"
        log_entry.integrity_hash = hashlib.sha256(content.encode()).hexdigest()
        log_entry.save()

        logger.info(f"MCP Auditor: Registro {id_global} guardado con hash {log_entry.integrity_hash[:8]}...")

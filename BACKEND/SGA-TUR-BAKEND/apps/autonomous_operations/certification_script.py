import uuid
from decimal import Decimal
from django.utils import timezone
from apps.autonomous_operations.models import AutonomousAgent, PolicyRule, DecisionProposal, AutonomousAction, AgentExecutionAudit
from apps.autonomous_operations.agent_registry import AgentRegistry
from apps.autonomous_operations.policy_engine import PolicyEngine
from apps.autonomous_operations.decision_engine import DecisionEngine
from apps.autonomous_operations.action_executor import ActionExecutor
from apps.autonomous_operations.learning_loop import LearningLoop
from apps.autonomous_operations.optimization_engine import OptimizationEngine
from apps.operational_intelligence.models import ChurnRiskScore, UnitEconomics

def run_certification():
    print("🚀 INICIANDO CERTIFICACIÓN FASE 6: OPERACIONES AUTÓNOMAS\n")

    # 1. Setup Environment
    # Clean previous test data
    DecisionProposal.objects.all().delete()
    AgentExecutionAudit.objects.all().delete()
    AutonomousAction.objects.all().delete()

    customer_id = uuid.uuid4()

    # Simulate high churn risk for a customer (from Phase 5)
    ChurnRiskScore.objects.filter(customer_id=customer_id).delete()
    ChurnRiskScore.objects.create(
        customer_id=customer_id,
        risk_score=Decimal('85.00'),
        risk_level='HIGH'
    )

    # 2. Decision Engine Test
    print("1. Activando Agente de Churn y generando propuesta...")
    agent = AutonomousAgent.objects.get(agent_code='churn-prevention')
    agent.status = 'ACTIVE'
    agent.autonomy_level = 'AUTOMATIC'
    agent.save()

    DecisionEngine.run_agent(agent)
    proposal = DecisionProposal.objects.filter(target_entity_id=customer_id).last()
    print(f"   - Propuesta generada: {proposal.proposed_action} (Confianza: {proposal.confidence_score}%)")
    assert proposal.proposed_action == 'APPLY_PREVENTIVE_DISCOUNT'

    # 3. Policy Engine Test (Violation)
    print("2. Verificando bloqueo por violación de política (Descuento excesivo)...")
    proposal.action_parameters['discount_rate'] = 0.50 # 50% exceeds 15% policy
    proposal.status = 'PENDING'
    proposal.save()

    ActionExecutor.evaluate_and_execute(proposal)
    proposal.refresh_from_db()
    print(f"   - Estado tras ejecución fallida: {proposal.status}")
    assert proposal.status == 'BLOCKED'

    # 4. Successful Execution Test
    print("3. Ejecutando acción automática válida...")
    proposal.status = 'PENDING'
    proposal.action_parameters['discount_rate'] = 0.10 # 10% is within 15% limit
    proposal.save()

    ActionExecutor.evaluate_and_execute(proposal)
    proposal.refresh_from_db()
    print(f"   - Estado tras ejecución exitosa: {proposal.status}")
    assert proposal.status == 'EXECUTED'

    action = AutonomousAction.objects.get(proposal=proposal)
    print(f"   - Hash de ejecución: {action.execution_hash[:10]}...")

    # 5. Learning Loop Test
    print("4. Verificando Learning Loop (Actualización de performance)...")
    prev_perf = agent.performance_score
    LearningLoop.measure_impact(action)
    agent.refresh_from_db()
    print(f"   - Performance anterior: {prev_perf} | Nueva: {agent.performance_score}")
    assert agent.performance_score > prev_perf

    # 6. Audit Traceability
    print("5. Verificando trazabilidad total (Audit Log)...")
    audits = AgentExecutionAudit.objects.filter(agent_code=agent.agent_code).order_by('timestamp')
    print(f"   - Pasos registrados: {[a.step for a in audits]}")
    assert audits.count() >= 3

    # 7. Reversibility Test
    print("6. Verificando reversibilidad de acciones...")
    ActionExecutor.revert_action(action.id)
    action.refresh_from_db()
    print(f"   - Acción revertida: {action.is_reverted}")
    assert action.is_reverted == True

    print("\n✅ CERTIFICACIÓN FASE 6 COMPLETADA CON ÉXITO")

if __name__ == "__main__":
    run_certification()

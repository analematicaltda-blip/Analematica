from typing import Any, Dict, Optional
import uuid
from django.utils import timezone
from django.utils.module_loading import import_string
from apps.admin_plataforma.models import GovernancePolicy # TODO: Move to service
from apps.sarita_agents.models import Mision, PlanTáctico # TODO: Move to service

class GovernanceService:
    """
    Service layer for AI Governance and Mission management.
    Ensures Agents don't touch ORM directly.
    """

    @staticmethod
    def record_agent_action(agent_code: str, action: str, service: str, params: Dict[str, Any], result: Any = None):
        from apps.core_erp.models import AgentActionAudit
        from apps.core_erp.observability.middleware import get_correlation_id

        return AgentActionAudit.objects.create(
            agent_code=agent_code,
            action=action,
            service_invoked=service,
            parameters=params,
            result=result,
            correlation_id=get_correlation_id()
        )

    @staticmethod
    def is_autonomy_suspended() -> bool:
        return GovernancePolicy.objects.filter(
            name__in=["KILL_SWITCH_AGENTS", "SYSTEM_ATTACK_MODE"],
            is_active=True
        ).exists()

    @staticmethod
    def create_mission(directive: Dict[str, Any], idempotency_key: Optional[str] = None):
        if idempotency_key and Mision.objects.filter(idempotency_key=idempotency_key).exists():
            raise ValueError("Directiva duplicada.")

        return Mision.objects.create(
            idempotency_key=idempotency_key,
            directiva_original=directive,
            dominio=directive.get("domain"),
            estado='EN_COLA'
        )

    @staticmethod
    def get_mission(mision_id: str):
        return Mision.objects.get(id=mision_id)

    @staticmethod
    def update_mission_status(mision_id: str, status: str, result: Optional[Dict[str, Any]] = None):
        mision = Mision.objects.get(id=mision_id)
        mision.estado = status
        if result:
            mision.resultado_final = result
        if status in ['EXITOSA', 'FALLIDA']:
            mision.timestamp_fin = timezone.now()
        mision.save()
        return mision

    @staticmethod
    def get_or_create_plan_tactico(mision, capitan_name: str):
        plan, _ = PlanTáctico.objects.get_or_create(
            misión=mision,
            capitán_asignado=capitan_name
        )
        return plan

    @staticmethod
    def save_plan_tactico(plan_id: str, steps: Dict[str, Any]):
        plan = PlanTáctico.objects.get(id=plan_id)
        plan.pasos_del_plan = steps
        plan.save()
        return plan

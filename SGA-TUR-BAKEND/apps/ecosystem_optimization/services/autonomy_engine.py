import logging
from typing import Dict, Any
from django.utils import timezone
from django.db import transaction
from apps.ecosystem_optimization.models import AutonomousAction, AutonomousExecutionLog, AutonomyControl
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel
from api.models import CustomUser

logger = logging.getLogger(__name__)

class AutonomyDenied(Exception):
    pass

class AutonomyEngine:
    """
    Motor de Autonomía de Sarita (Fase F-F).
    Regula, valida y audita acciones ejecutadas por la IA sin intervención humana directa.
    """

    @classmethod
    def execute_autonomous_action(cls, action_name: str, parameters: Dict[str, Any], actor_user: CustomUser = None) -> Dict[str, Any]:
        """
        Punto de entrada para la ejecución autónoma delegada.
        """
        try:
            # 1. Identificar Acción
            action = AutonomousAction.objects.get(name=action_name, is_active=True)

            # 2. Verificar Nivel de Autonomía (Punto 1.2)
            if action.autonomy_level < AutonomousAction.Level.AUTONOMA_CONDICIONADA:
                raise AutonomyDenied(f"Acción '{action_name}' requiere confirmación humana (Nivel < 2).")
            if action.autonomy_level >= AutonomousAction.Level.AUTONOMA_SOBERANA:
                 raise AutonomyDenied(f"Acción '{action_name}' está en Nivel Soberano (Protegido).")

            # 3. Verificar Kill Switches (Punto 6)
            cls._check_kill_switches(action.domain)

            # 4. Verificar Límites Hard (Punto 4)
            cls._check_hard_limits(action, parameters)

            # 5. Validación GRC Sistémica (Punto 3)
            # Usamos el Kernel de Gobernanza para asegurar que la acción cumpla las políticas globales.
            # Nota: Si no se provee actor_user, se asume un contexto de sistema con autoridad delegada.
            kernel_user = actor_user or CustomUser.objects.filter(role=CustomUser.Role.ADMIN, is_superuser=True).first()
            kernel = GovernanceKernel(kernel_user)

            # 6. Generar Explicación XAI (Punto 7)
            explanation = cls._generate_explanation(action, parameters)

            # 7. Ejecución Atómica
            with transaction.atomic():
                # En Sarita, las intenciones del Kernel son el lenguaje universal de ejecución.
                result = kernel.resolve_and_execute(
                    intention_name=action_name,
                    parameters=parameters,
                    bypass_policy=False # La IA NUNCA ignora políticas
                )

                # 8. Registro y Auditoría Total (Punto 9)
                AutonomousExecutionLog.objects.create(
                    action=action,
                    explanation=explanation,
                    data_points=parameters,
                    policy_applied=action.policy_reference,
                    result_status='SUCCESS',
                    impact_measured={'result': result}
                )

                return {
                    "status": "SUCCESS",
                    "action": action_name,
                    "explanation": explanation,
                    "result": result
                }

        except AutonomousAction.DoesNotExist:
            logger.error(f"AUTONOMY: Acción '{action_name}' no existe o no está activa.")
            raise AutonomyDenied(f"Acción '{action_name}' no tipificada para autonomía.")
        except AutonomyDenied as e:
            logger.warning(f"AUTONOMY BLOCKED: {str(e)}")
            cls._log_failure(action_name, str(e), parameters, 'BLOCKED')
            raise e
        except Exception as e:
            logger.error(f"AUTONOMY ERROR: {str(e)}")
            cls._log_failure(action_name, str(e), parameters, 'FAILED')
            raise e

    @classmethod
    def _check_kill_switches(cls, domain: str):
        # Global Kill Switch (domain=None)
        global_control = AutonomyControl.objects.filter(domain__isnull=True).first()
        if global_control and not global_control.is_enabled:
            raise AutonomyDenied(f"KILL SWITCH GLOBAL ACTIVADO: {global_control.reason}")

        # Domain Kill Switch
        domain_control = AutonomyControl.objects.filter(domain=domain).first()
        if domain_control and not domain_control.is_enabled:
            raise AutonomyDenied(f"KILL SWITCH DOMINIO '{domain}' ACTIVADO: {domain_control.reason}")

    @classmethod
    def _check_hard_limits(cls, action: AutonomousAction, params: Dict[str, Any]):
        # 1. Límite de ejecuciones diarias (Punto 4.1)
        today_executions = AutonomousExecutionLog.objects.filter(
            action=action,
            timestamp__date=timezone.now().date(),
            result_status='SUCCESS'
        ).count()

        if today_executions >= action.max_daily_executions:
            raise AutonomyDenied(f"Límite diario de ejecuciones superado ({action.max_daily_executions}).")

        # 2. Límite de impacto financiero (Si aplica)
        amount = params.get('amount') or params.get('precio') or params.get('valor')
        if amount and action.max_financial_impact > 0:
            if float(amount) > float(action.max_financial_impact):
                 raise AutonomyDenied(f"Impacto financiero ({amount}) excede el límite autónomo ({action.max_financial_impact}).")

    @classmethod
    def _generate_explanation(cls, action: AutonomousAction, params: Dict[str, Any]) -> str:
        """
        Implementa XAI (Explainable AI) - Punto 7.
        Genera una narrativa técnica-humana del porqué de la acción.
        """
        return (
            f"Se ejecuta la acción '{action.name}' en el dominio {action.domain} "
            f"porque se detectó una oportunidad de optimización con parámetros {params}. "
            f"Esta decisión se basa en la política '{action.policy_reference}' "
            f"y se mantiene dentro de los umbrales de seguridad pre-autorizados (Nivel 2)."
        )

    @classmethod
    def _log_failure(cls, action_name: str, reason: str, params: Dict[str, Any], status: str):
        try:
            action = AutonomousAction.objects.get(name=action_name)
            AutonomousExecutionLog.objects.create(
                action=action,
                explanation=f"EJECUCIÓN FALLIDA/BLOQUEADA: {reason}",
                data_points=params,
                policy_applied="N/A",
                result_status=status,
                was_interrupted=True if status == 'BLOCKED' else False
            )
        except:
            pass

import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico, TareaDelegada

logger = logging.getLogger(__name__)

class CapitanMonederoBase(CapitanTemplate):
    """Base para capitanes de monedero que permite ejecución síncrona en este entorno."""
    def delegate(self, plan: PlanTáctico):
        logger.info(f"CAPITÁN ({self.__class__.__name__}): Ejecutando plan {plan.id} de forma síncrona para cierre estructural.")
        plan.estado = 'EN_EJECUCION'
        plan.save()

        for _, tarea_info in plan.pasos_del_plan.items():
            teniente_name = tarea_info.get("teniente")
            # En un entorno real esto usaría el roster y Celery.
            # Aquí instanciamos y ejecutamos directamente para validar el flujo FE-BE.
            from .tenientes import (
                TenienteValidacionSaldo,
                TenienteAutorizacionTransferencias,
                TenienteControlLimites,
                TenienteEvidenciasFinancieras,
                TenienteMonitoreoRiesgo
            )
            roster = {
                "validacion_saldo": TenienteValidacionSaldo(),
                "autorizacion_transferencias": TenienteAutorizacionTransferencias(),
                "control_limites": TenienteControlLimites(),
                "evidencias_financieras": TenienteEvidenciasFinancieras(),
                "monitoreo_riesgo": TenienteMonitoreoRiesgo()
            }

            teniente = roster.get(teniente_name)
            if teniente:
                tarea = TareaDelegada.objects.create(
                    plan_tactico=plan,
                    teniente_asignado=teniente_name,
                    descripcion_tarea=tarea_info.get("descripcion", "N/A"),
                    parametros=tarea_info.get("parametros", {}),
                    estado='EN_PROGRESO'
                )
                teniente.execute_task(tarea)

        plan.estado = 'COMPLETADO'
        plan.save()

class CapitanCustodiaFondos(CapitanMonederoBase):
    def _get_tenientes(self) -> dict:
        return {"validacion_saldo": "TenienteValidacionSaldo"}

    def plan(self, mision) -> PlanTáctico:
        plan = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        plan.pasos_del_plan = {
            "paso_1": {
                "teniente": "validacion_saldo",
                "descripcion": "Verificar integridad de saldos en la cuenta",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }
        plan.save()
        return plan

class CapitanAntifraude(CapitanMonederoBase):
    def _get_tenientes(self) -> dict:
        return {"monitoreo_riesgo": "TenienteMonitoreoRiesgo"}

    def plan(self, mision) -> PlanTáctico:
        plan = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        plan.pasos_del_plan = {
            "paso_1": {
                "teniente": "monitoreo_riesgo",
                "descripcion": "Analizar patrones de movimientos sospechosos",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }
        plan.save()
        return plan

class CapitanTransferencias(CapitanMonederoBase):
    def _get_tenientes(self) -> dict:
        return {
            "autorizacion_transferencias": "TenienteAutorizacionTransferencias",
            "control_limites": "TenienteControlLimites"
        }

    def plan(self, mision) -> PlanTáctico:
        plan = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        plan.pasos_del_plan = {
            "paso_1": {
                "teniente": "control_limites",
                "descripcion": "Verificar límites de transferencia por rol",
                "parametros": mision.directiva_original.get("parameters", {})
            },
            "paso_2": {
                "teniente": "autorizacion_transferencias",
                "descripcion": "Autorizar movimiento entre carteras",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }
        plan.save()
        return plan

class CapitanPagosServicios(CapitanMonederoBase):
    def _get_tenientes(self) -> dict:
        return {"validacion_servicio": "TenienteValidacionServicio"}

    def plan(self, mision) -> PlanTáctico:
        plan = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        plan.pasos_del_plan = {
            "paso_1": {
                "teniente": "validacion_servicio",
                "descripcion": "Validar existencia y estado del servicio a pagar",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }
        plan.save()
        return plan

class CapitanLiquidaciones(CapitanMonederoBase):
    def _get_tenientes(self) -> dict:
        return {"ejecucion_liquidacion": "TenienteEjecucionLiquidacion"}

    def plan(self, mision) -> PlanTáctico:
        plan = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        plan.pasos_del_plan = {
            "paso_1": {
                "teniente": "ejecucion_liquidacion",
                "descripcion": "Preparar orden de pago financiera",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }
        plan.save()
        return plan

class CapitanAuditoriaFinanciera(CapitanMonederoBase):
    def _get_tenientes(self) -> dict:
        return {"evidencias_financieras": "TenienteEvidenciasFinancieras"}

    def plan(self, mision) -> PlanTáctico:
        plan = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        plan.pasos_del_plan = {
            "paso_1": {
                "teniente": "evidencias_financieras",
                "descripcion": "Generar pruebas de integridad de la transacción",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }
        plan.save()
        return plan

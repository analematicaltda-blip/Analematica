import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanTesoreria(CapitanTemplate):
    """
    Capitán especializado en la gestión de Tesorería.
    """
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {
            "1": {"teniente": "auditoria_saldos", "descripcion": "Auditar saldos en todas las cuentas de custodia."},
            "2": {"teniente": "conciliacion", "descripcion": "Ejecutar conciliación de tesorería central."}
        }
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanCustodiaFondos(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "verificacion_custodia", "descripcion": "Verificar integridad de fondos en bóveda digital."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanLiquidez(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "calculo_liquidez", "descripcion": "Calcular ratios de liquidez inmediata."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanPagos(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {
            "1": {"teniente": "autorizacion", "descripcion": "Validar autorización de la orden de pago."},
            "2": {"teniente": "ejecucion_sargento", "descripcion": "Delegar al sargento la transferencia real."}
        }
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanDistribucion(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "reparto_fondos", "descripcion": "Calcular distribución de ingresos según reglas de negocio."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanReservas(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "provision_reservas", "descripcion": "Asegurar el traslado de fondos a cuentas de reserva."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanProyecciones(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "simulacion_escenarios", "descripcion": "Generar proyecciones financieras basadas en histórico."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanCumplimientoFinanciero(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "check_normativo", "descripcion": "Verificar cumplimiento de normatividad financiera."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanEstadoResultados(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "compilacion_pyg", "descripcion": "Compilar ingresos y gastos para el P&L."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanBalanceGeneral(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "foto_patrimonial", "descripcion": "Generar balance de activos, pasivos y patrimonio."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanFlujoEfectivo(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "analisis_cashflow", "descripcion": "Analizar entradas y salidas de efectivo reales."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanCambiosPatrimonio(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "evolucion_patrimonio", "descripcion": "Registrar variaciones en el capital contable."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanConciliacionBancaria(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "cruce_extractos", "descripcion": "Cruzar movimientos bancarios con registros internos."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanProvisionesFinancieras(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "calculo_provisiones", "descripcion": "Calcular y bloquear montos para futuras obligaciones."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from apps.sarita_agents.models import TareaDelegada
from ..sargentos.sargento_municipal import SargentoGobiernoMunicipal
from ..soldados.soldados_municipales import SoldadoAuditorLocal, SoldadoInspectorRNT

class TenientecontrolPrestadores(TenienteTemplate):
    """
    Teniente encargado de la supervisión y control de prestadores locales.
    Coordina al sargento y soldados para verificar cumplimiento.
    """
    def execute_task(self, tarea: TareaDelegada):
        self.logger.info(f"TENIENTE {self.__class__.__name__}: Iniciando supervisión de prestadores.")

        # 1. Acción de Negocio vía Sargento
        sargento = SargentoGobiernoMunicipal(teniente=self)
        sargento_report = sargento.handle_mission(tarea.parametros_especificos)

        # 2. Acción Operativa vía Soldados
        soldado_auditor = SoldadoAuditorLocal()
        audit_result = soldado_auditor.perform_action(tarea.parametros_especificos)

        soldado_rnt = SoldadoInspectorRNT()
        rnt_result = soldado_rnt.perform_action(tarea.parametros_especificos)

        resultado = {
            "status": "SUCCESS",
            "sargento_report": sargento_report,
            "audit": audit_result,
            "rnt": rnt_result
        }
        self.mark_task_as_success(tarea, str(resultado))

from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from .sargentos import (
    SargentoAsignaciones, SargentoValidacionInventario, SargentoPrioridades,
    SargentoOptimizacion, SargentoReasignacion, SargentoControlTiempos,
    SargentoFlota, SargentoIncidentesConductores, SargentoKPIs, SargentoSLAs
)

class TenienteDespacho(TenienteTemplate):
    def perform_action(self, parametros: dict):
        s1 = SargentoAsignaciones(teniente=self)
        s2 = SargentoValidacionInventario(teniente=self)
        s3 = SargentoPrioridades(teniente=self)

        # Simulación de ejecución en cadena
        s2.handle_order(parametros)
        s3.handle_order(parametros)
        return s1.handle_order(parametros)

class TenienteRutas(TenienteTemplate):
    def perform_action(self, parametros: dict):
        s1 = SargentoOptimizacion(teniente=self)
        s2 = SargentoReasignacion(teniente=self)
        s3 = SargentoControlTiempos(teniente=self)

        s1.handle_order(parametros)
        s3.handle_order(parametros)
        return {"status": "ROUTES_OPTIMIZED"}

class TenienteRepartidores(TenienteTemplate):
    def perform_action(self, parametros: dict):
        s1 = SargentoFlota(teniente=self)
        s2 = SargentoIncidentesConductores(teniente=self)
        return s1.handle_order(parametros)

class TenienteSeguimiento(TenienteTemplate):
    def perform_action(self, parametros: dict):
        # El seguimiento suele ser reactivo o consulta de estado
        return {"tracking_status": "ACTIVE", "realtime_enabled": True}

class TenienteIndicadores(TenienteTemplate):
    def perform_action(self, parametros: dict):
        s1 = SargentoKPIs(teniente=self)
        s2 = SargentoSLAs(teniente=self)
        s2.handle_order(parametros)
        return s1.handle_order(parametros)

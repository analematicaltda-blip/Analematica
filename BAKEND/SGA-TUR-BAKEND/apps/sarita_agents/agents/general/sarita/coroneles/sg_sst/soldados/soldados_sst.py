from apps.sarita_agents.agents.soldado_n6_oro_v2 import SoldadoN6OroV2
import logging

logger = logging.getLogger(__name__)

class SoldadoRiesgos(SoldadoN6OroV2):
    domain = "sg_sst"
    aggregate_root = "EvaluacionRiesgo"
    required_permissions = ["sg_sst.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO RIESGOS: Evaluando factor de riesgo.")
        from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.models import EvaluacionRiesgo

        riesgo = EvaluacionRiesgo.objects.create(
            provider_id=params.get('provider_id'),
            factor_riesgo=params.get('factor'),
            nivel_riesgo=params.get('nivel', 'BAJO'),
            controles_sugeridos=params.get('controles', 'Ninguno')
        )
        return riesgo

class SoldadoIncidentes(SoldadoN6OroV2):
    domain = "sg_sst"
    aggregate_root = "IncidenteLaboral"
    required_permissions = ["sg_sst.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO INCIDENTES: Registrando incidente.")
        from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.models import IncidenteLaboral

        incidente = IncidenteLaboral.objects.create(
            provider_id=params.get('provider_id'),
            descripcion=params.get('descripcion'),
            fecha_incidente=params.get('fecha'),
            gravedad=params.get('gravedad', 'LEVE')
        )
        return incidente

class SoldadoCapacitacion(SoldadoN6OroV2):
    domain = "sg_sst"
    aggregate_root = "CapacitacionSST"
    required_permissions = ["sg_sst.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO CAPACITACION: Verificando asistencia.")
        from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.models import CapacitacionSST

        cap = CapacitacionSST.objects.create(
            provider_id=params.get('provider_id'),
            tema=params.get('tema'),
            fecha_ejecucion=params.get('fecha'),
            asistentes_count=params.get('asistentes', 0)
        )
        return cap

class SoldadoInspecciones(SoldadoN6OroV2):
    domain = "sg_sst"
    aggregate_root = "InspeccionSeguridad"
    required_permissions = ["sg_sst.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO INSPECCIONES: Ejecutando inspección.")
        from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.models import InspeccionSeguridad

        inspeccion = InspeccionSeguridad.objects.create(
            provider_id=params.get('provider_id'),
            area=params.get('area'),
            hallazgos=params.get('hallazgos', 'Sin hallazgos'),
            cumple=params.get('cumple', True)
        )
        return inspeccion

class SoldadoIndicadores(SoldadoN6OroV2):
    domain = "sg_sst"
    aggregate_root = "IndicadorSST"
    required_permissions = ["sg_sst.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO INDICADORES: Procesando datos SST.")
        from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.models import IndicadorSST

        ind = IndicadorSST.objects.create(
            provider_id=params.get('provider_id'),
            nombre=params.get('nombre'),
            valor=params.get('valor', 0.0),
            periodo=params.get('periodo')
        )
        return ind

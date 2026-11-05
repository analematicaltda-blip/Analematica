# backend/apps/sarita_agents/agents/general/sarita/coroneles/operativo_general/coronel.py
import logging
from apps.sarita_agents.agents.coronel_template import CoronelTemplate

class CoronelOperativoGeneral(CoronelTemplate):
    """
    Coronel Operativo General: Gobierna toda la política operativa genérica del sistema SARITA.
    """
    def __init__(self, general):
        super().__init__(general=general, domain="operativo_general")

    def _get_capitanes(self) -> dict:
        # Importaciones tardías para evitar circulares
        from .capitanes.capitan_creacion_ordenes import CapitanCreacionOrdenes
        from .capitanes.capitan_transiciones_estado import CapitanTransicionesEstado
        from .capitanes.capitan_cancelacion_ordenes import CapitanCancelacionOrdenes
        from .capitanes.capitan_vinculacion_contrato import CapitanVinculacionContrato
        from .capitanes.capitan_validacion_disponibilidad import CapitanValidacionDisponibilidad
        from .capitanes.capitan_asignacion_recursos import CapitanAsignacionRecursos
        from .capitanes.capitan_consumo_inventario import CapitanConsumoInventario
        from .capitanes.capitan_bloqueo_agotamiento import CapitanBloqueoAgotamiento
        from .capitanes.capitan_gestion_turnos import CapitanGestionTurnos
        from .capitanes.capitan_excepciones_horario import CapitanExcepcionesHorario
        from .capitanes.capitan_registro_costos_reales import CapitanRegistroCostosReales
        from .capitanes.capitan_costos_mano_obra import CapitanCostosManoObra
        from .capitanes.capitan_costos_insumos import CapitanCostosInsumos
        from .capitanes.capitan_impacto_contable_operativo import CapitanImpactoContableOperativo
        from .capitanes.capitan_evidencia_documental import CapitanEvidenciaDocumental
        from .capitanes.capitan_evidencia_visual import CapitanEvidenciaVisual
        from .capitanes.capitan_integridad_evidencia import CapitanIntegridadEvidencia
        from .capitanes.capitan_s_l_a_operativo import CapitanSLAOperativo
        from .capitanes.capitan_productividad_agentes import CapitanProductividadAgentes
        from .capitanes.capitan_configuracion_capacidad import CapitanConfiguracionCapacidad
        from .capitanes.capitan_gestion_incidencias import CapitanGestionIncidencias
        from .capitanes.capitan_feedback_post_servicio import CapitanFeedbackPostServicio
        from .capitanes.capitan_reprogramacion_emergencia import CapitanReprogramacionEmergencia

        return {
            "creacion_ordenes": CapitanCreacionOrdenes(coronel=self),
            "transiciones_estado": CapitanTransicionesEstado(coronel=self),
            "cancelacion_ordenes": CapitanCancelacionOrdenes(coronel=self),
            "vinculacion_contrato": CapitanVinculacionContrato(coronel=self),
            "validacion_disponibilidad": CapitanValidacionDisponibilidad(coronel=self),
            "asignacion_recursos": CapitanAsignacionRecursos(coronel=self),
            "consumo_inventario": CapitanConsumoInventario(coronel=self),
            "bloqueo_agotamiento": CapitanBloqueoAgotamiento(coronel=self),
            "gestion_turnos": CapitanGestionTurnos(coronel=self),
            "excepciones_horario": CapitanExcepcionesHorario(coronel=self),
            "registro_costos": CapitanRegistroCostosReales(coronel=self),
            "costos_mano_obra": CapitanCostosManoObra(coronel=self),
            "costos_insumos": CapitanCostosInsumos(coronel=self),
            "impacto_contable": CapitanImpactoContableOperativo(coronel=self),
            "evidencia_documental": CapitanEvidenciaDocumental(coronel=self),
            "evidencia_visual": CapitanEvidenciaVisual(coronel=self),
            "integridad_evidencia": CapitanIntegridadEvidencia(coronel=self),
            "sla_operativo": CapitanSLAOperativo(coronel=self),
            "productividad_agentes": CapitanProductividadAgentes(coronel=self),
            "configuracion_capacidad": CapitanConfiguracionCapacidad(coronel=self),
            "gestion_incidencias": CapitanGestionIncidencias(coronel=self),
            "feedback_post_servicio": CapitanFeedbackPostServicio(coronel=self),
            "reprogramacion_emergencia": CapitanReprogramacionEmergencia(coronel=self),
        }

    def _select_capitan(self, directiva: dict):
        m_type = directiva.get("mission", {}).get("type")

        mapping = {
            "CREATE_OPERATIONAL_ORDER": "creacion_ordenes",
            "TRANSITION_OPERATIONAL_STATE": "transiciones_estado",
            "CANCEL_OPERATIONAL_ORDER": "cancelacion_ordenes",
            "LINK_CONTRACT_TO_ORDER": "vinculacion_contrato",
            "VALIDATE_AVAILABILITY": "validacion_disponibilidad",
            "ASSIGN_OPERATIONAL_RESOURCE": "asignacion_recursos",
            "CONSUME_INVENTORY": "consumo_inventario",
            "REPORT_OPERATIONAL_INCIDENT": "gestion_incidencias",
            "RECORD_OPERATIONAL_COST": "registro_costos",
            "COLLECT_OPERATIONAL_EVIDENCE": "evidencia_visual",
        }

        cap_key = mapping.get(m_type)
        if cap_key:
            return self.capitanes.get(cap_key)

        # Fallback
        return self.capitanes.get("creacion_ordenes")

import logging
from apps.sarita_agents.agents.coronel_template import CoronelTemplate
from apps.sarita_agents.agents.general.sarita.coroneles.prestadores.capitanes.gestion_operativa.sg_sst.capitan_sst import CapitanSST
from apps.sarita_agents.agents.general.sarita.coroneles.prestadores.capitanes.gestion_operativa.sg_sst.capitan_incidentes_sst import CapitanIncidentesSST
from apps.sarita_agents.agents.general.sarita.coroneles.prestadores.capitanes.gestion_operativa.sg_sst.capitan_normativo_sst import CapitanNormativoSST
from apps.sarita_agents.agents.general.sarita.coroneles.prestadores.capitanes.gestion_operativa.sg_sst.capitanes_sst_especializados import (
    CapitanIdentificacionPeligros, CapitanEvaluacionRiesgos, CapitanSaludOcupacional,
    CapitanRiesgoPsicosocial, CapitanEmergencias, CapitanCapacitacionSST, CapitanVigilanciaSST
)

logger = logging.getLogger(__name__)

class CoronelSST(CoronelTemplate):
    """
    Coronel SG-SST General: Gobierna integralmente la política de seguridad y salud en el trabajo.
    """
    def _get_capitanes(self) -> dict:
        return {
            "sst_general": CapitanSST(coronel=self),
            "sst_incidentes": CapitanIncidentesSST(coronel=self),
            "sst_normativo": CapitanNormativoSST(coronel=self),
            "sst_peligros": CapitanIdentificacionPeligros(coronel=self),
            "sst_evaluacion": CapitanEvaluacionRiesgos(coronel=self),
            "sst_salud": CapitanSaludOcupacional(coronel=self),
            "sst_psicosocial": CapitanRiesgoPsicosocial(coronel=self),
            "sst_emergencias": CapitanEmergencias(coronel=self),
            "sst_capacitacion": CapitanCapacitacionSST(coronel=self),
            "sst_vigilancia": CapitanVigilanciaSST(coronel=self),
        }

    def _select_capitan(self, directiva: dict):
        m_type = directiva.get("mission", {}).get("type")
        mapping = {
            "IDENTIFY_HAZARDS": "sst_peligros",
            "EVALUATE_SST_RISK": "sst_evaluacion",
            "REGISTER_SST_INCIDENT": "sst_incidentes",
            "MANAGE_SST_EMERGENCY": "sst_emergencias",
            "AUDIT_SST_COMPLIANCE": "sst_normativo",
            "HEALTH_CHECK": "sst_salud",
            "PSYCHOSOCIAL_EVAL": "sst_psicosocial",
            "TRAINING_SST": "sst_capacitacion",
            "VIGILANCE_SST": "sst_vigilancia",
        }
        cap_key = mapping.get(m_type, "sst_general")
        return self.capitanes.get(cap_key)

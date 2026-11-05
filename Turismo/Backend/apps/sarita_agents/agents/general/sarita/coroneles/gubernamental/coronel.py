# backend/apps/sarita_agents/agents/general/sarita/coroneles/gubernamental/coronel.py

from .....coronel_template import CoronelTemplate
from .municipal.capitanes.capitan_turismo_local import CapitanTurismoLocal
from .municipal.capitanes.capitan_control_prestadores import CapitanControlPrestadores
from .municipal.capitanes.capitan_eventos_locales import CapitanEventosLocales
from .departamental.capitanes.capitan_planificacion_regional import CapitanPlanificacionRegional
from .departamental.capitanes.capitan_rutas_turisticas import CapitanRutasTuristicas
from .departamental.capitanes.capitan_coordinacion_municipal import CapitanCoordinacionMunicipal
from .nacional.capitanes.capitan_politicas_nacionales import CapitanPoliticasNacionales
from .nacional.capitanes.capitan_indicadores_nacionales import CapitanIndicadoresNacionales
from .nacional.capitanes.capitan_estandares_certificaciones import CapitanEstandaresCertificaciones

class GubernamentalCoronel(CoronelTemplate):
    """
    Coronel de Gobierno y Cumplimiento Normativo.
    Gobierna la relación con Secretarías, Direcciones de Turismo y Entidades Nacionales.
    """
    def __init__(self, general):
        super().__init__(general=general, domain="gubernamental")

    def _get_capitanes(self) -> dict:
        return {
            # Municipal
            "turismo_local": CapitanTurismoLocal(coronel=self),
            "control_prestadores": CapitanControlPrestadores(coronel=self),
            "eventos_locales": CapitanEventosLocales(coronel=self),
            # Departamental
            "planificacion_regional": CapitanPlanificacionRegional(coronel=self),
            "rutas_regionales": CapitanRutasTuristicas(coronel=self),
            "coordinacion_municipal": CapitanCoordinacionMunicipal(coronel=self),
            # Nacional
            "politicas_nacionales": CapitanPoliticasNacionales(coronel=self),
            "indicadores_macro": CapitanIndicadoresNacionales(coronel=self),
            "certificaciones": CapitanEstandaresCertificaciones(coronel=self),
        }

    def _select_capitan(self, directiva: dict):
        m_type = directiva.get("mission", {}).get("type")

        # Mapeo de misiones gubernamentales
        mapping = {
            "AUDIT_LOCAL_COMPLIANCE": "control_prestadores",
            "MANAGE_LOCAL_EVENTS": "eventos_locales",
            "GENERATE_REGIONAL_ROUTE": "rutas_regionales",
            "UPDATE_NATIONAL_INDICATORS": "indicadores_macro",
            "VERIFY_CERTIFICATION": "certificaciones",
        }

        return self.capitanes.get(mapping.get(m_type))

import logging
from apps.sarita_agents.agents.coronel_template import CoronelTemplate

class CoronelOperativaTuristica(CoronelTemplate):
    """
    Coronel Unificado de Operativa Turística.
    Gestiona tanto Operadores Directos como Cadena Productiva (Artesanos).
    """
    def __init__(self, general):
        super().__init__(general=general, domain="operativa_turistica")

    def _get_capitanes(self) -> dict:
        # Aquí se integran los capitanes de todos los subdominios
        from .directos.agencias.capitanes.capitan_agencia import CapitanAgencia
        from .directos.transporte.capitanes.capitan_despacho_flota import CapitanDespachoFlota
        from .directos.transporte.capitanes.capitan_monitoreo_rutas import CapitanMonitoreoRutas
        from .directos.guias.capitanes.capitan_gestion_guias import CapitanGestionGuias
        from .directos.hospedaje.capitanes.capitan_gestion_habitaciones import CapitanGestionHabitaciones
        from .directos.hospedaje.capitanes.capitan_checkin_checkout import CapitanCheckInCheckOut
        from .directos.gastronomia.capitanes.capitan_servicio_mesa import CapitanServicioMesa
        from .directos.gastronomia.capitanes.capitan_operacion_cocina import CapitanOperacionCocina
        from .directos.nocturno.capitanes.capitan_operacion_nocturna import CapitanOperacionNocturna
        # Capitán de Artesanos (Cadena Productiva)
        from .cadena_productiva.artesanos.capitanes.capitan_artesanos import CapitanArtesanos

        return {
            "agencia": CapitanAgencia(coronel=self),
            "transporte": CapitanDespachoFlota(coronel=self),
            "monitoreo_rutas": CapitanMonitoreoRutas(coronel=self),
            "guias": CapitanGestionGuias(coronel=self),
            "habitaciones": CapitanGestionHabitaciones(coronel=self),
            "checkin_checkout": CapitanCheckInCheckOut(coronel=self),
            "servicio_mesa": CapitanServicioMesa(coronel=self),
            "cocina": CapitanOperacionCocina(coronel=self),
            "nocturno": CapitanOperacionNocturna(coronel=self),
            "artesanos": CapitanArtesanos(coronel=self),
        }

    def _select_capitan(self, directiva: dict):
        # S-1: Extracción de tipo de misión (soporta directiva plana o anidada)
        mision_obj = directiva.get("mission")
        if isinstance(mision_obj, dict):
            m_type = mision_obj.get("type")
        else:
            m_type = directiva.get("action") # Fallback para algunas implementaciones

        # Mapeo de misiones a capitanes
        if m_type in ["CREATE_PACKAGE", "BOOK_PACKAGE", "CANCEL_PACKAGE_COMPONENT", "LIQUIDATE_AGENCY_PACKAGE"]:
            return self.capitanes.get("agencia")
        if m_type in ["DISPATCH_VEHICLE", "SCHEDULE_TRANSPORT_TRIP", "BOOK_TRANSPORT_SEAT", "LIQUIDATE_TRANSPORT_TRIP"]:
            return self.capitanes.get("transporte")
        if m_type == "UPDATE_ROUTE_PROGRESS":
            return self.capitanes.get("monitoreo_rutas")
        if m_type in ["ASSIGN_GUIDE", "LIQUIDATE_GUIDE_COMMISSION"]:
            return self.capitanes.get("guias")
        if m_type == "UPDATE_ROOM_STATUS":
            return self.capitanes.get("habitaciones")
        if m_type in ["EXECUTE_CHECK_IN", "EXECUTE_CHECK_OUT"]:
            return self.capitanes.get("checkin_checkout")
        if m_type == "MANAGE_TABLES":
            return self.capitanes.get("servicio_mesa")
        if m_type == "PROCESS_KITCHEN_ORDER":
            return self.capitanes.get("cocina")
        if m_type in ["PROCESS_COMMAND", "BILL_CONSUMPTION", "NIGHT_CASH_CLOSE", "VOID_CONSUMPTION"]:
            return self.capitanes.get("nocturno")
        if m_type in ["MANAGE_WORKSHOP", "REGISTER_PRODUCTION", "UPDATE_ARTISAN_INVENTORY", "SYNC_PRODUCTION_CATALOG"]:
            return self.capitanes.get("artesanos")

        return None

import logging
from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from django.utils.module_loading import import_string
SargentoEspecializado = import_string('apps.prestadores.mi_negocio.gestion_operativa.sargentos_especializados.SargentoEspecializado') # DECOUPLED

logger = logging.getLogger(__name__)

# Instancia compartida de sargento (singleton pattern simbólico)
sargento_especializado = SargentoEspecializado()

class TenienteOperativoHospedaje(TenienteTemplate):
    def perform_action(self, parametros: dict):
        habitacion_id = parametros.get("habitacion_id")
        nuevo_estado = parametros.get("nuevo_estado")
        provider_id = parametros.get("provider_id")

        logger.info(f"TENIENTE HOSPEDAJE: Solicitando actualización para Hab {habitacion_id} -> {nuevo_estado} (Provider: {provider_id})")

        exito = sargento_especializado.actualizar_estado_habitacion(
            provider_id=provider_id,
            habitacion_id=habitacion_id,
            nuevo_estado=nuevo_estado
        )

        if exito:
            return {"status": "SUCCESS", "entity": "Room", "id": habitacion_id}
        else:
            raise Exception(f"Sargento no pudo completar la acción para Habitación {habitacion_id}")

class TenienteOperativoGastronomia(TenienteTemplate):
    def perform_action(self, parametros: dict):
        mesa_id = parametros.get("mesa_id")
        accion = parametros.get("accion", "PROCESS_COMMAND")
        logger.info(f"TENIENTE GASTRONOMIA: Ejecutando {accion} para Mesa {mesa_id}")

        from django.utils.module_loading import import_string
        SargentoRestaurante = import_string('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.restaurantes.sargentos.SargentoRestaurante')

        from api.models import CustomUser
        user = CustomUser.objects.get(id=parametros.get("user_id"))

        if accion == "PROCESS_COMMAND":
            return SargentoRestaurante.procesar_comanda(parametros, user)
        if accion == "BILL_CONSUMPTION":
            return SargentoRestaurante.facturar_mesa(parametros, user)

        return {"status": "SUCCESS", "entity": "RestaurantTable", "id": mesa_id}

class TenienteOperativoTransporte(TenienteTemplate):
    def perform_action(self, parametros: dict):
        action = parametros.get("action")
        from django.utils.module_loading import import_string
        SargentoTransporte = import_string('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.transporte.sargentos.SargentoTransporte')

        from api.models import CustomUser

        user_id = parametros.get("user_id")
        user = CustomUser.objects.get(id=user_id) if user_id else None

        if action == "SCHEDULE_TRANSPORT_TRIP":
            return SargentoTransporte.programar_y_asignar(parametros, user)
        if action == "BOOK_TRANSPORT_SEAT":
            return SargentoTransporte.registrar_reserva_masiva(parametros, user)
        if action == "LIQUIDATE_TRANSPORT_TRIP":
            return SargentoTransporte.liquidar_servicio_transporte(parametros, user)

        # Fallback para despacho antiguo si es necesario
        vehiculo_id = parametros.get("vehiculo_id")
        ruta_id = parametros.get("ruta_id")
        logger.info(f"TENIENTE TRANSPORTE: Despachando {vehiculo_id} en ruta {ruta_id}")
        return {"status": "SUCCESS", "entity": "Vehicle", "id": vehiculo_id}

class TenienteOperativoNocturno(TenienteTemplate):
    def perform_action(self, parametros: dict):
        action = parametros.get("action")
        from django.utils.module_loading import import_string
        SargentoNocturno = import_string('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.restaurantes.sargentos.SargentoRestaurante')

        from api.models import CustomUser

        user = CustomUser.objects.get(id=parametros.get("user_id"))

        if action == "PROCESS_COMMAND":
            return SargentoNocturno.procesar_comanda(parametros, user)
        if action == "BILL_CONSUMPTION":
            return SargentoNocturno.facturar_mesa(parametros, user)
        if action == "VOID_CONSUMPTION":
            return SargentoNocturno.anular_consumo(parametros, user)
        if action == "NIGHT_CASH_CLOSE":
            return SargentoNocturno.cerrar_caja(parametros, user)

        return {"status": "ERROR", "message": "Acción no reconocida"}

class TenienteOperativoGuias(TenienteTemplate):
    def perform_action(self, parametros: dict):
        action = parametros.get("action")
        from django.utils.module_loading import import_string
        SargentoGuias = import_string('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.guias.sargentos.SargentoGuias')

        from api.models import CustomUser

        user = CustomUser.objects.get(id=parametros.get("user_id"))

        if action == "ASSIGN_GUIDE":
            return SargentoGuias.asignar_y_confirmar(parametros, user)
        if action == "LIQUIDATE_GUIDE_COMMISSION":
            return SargentoGuias.liquidar_comision(parametros, user)

        return {"status": "ERROR", "message": "Acción no reconocida"}

class TenienteOperativoAgencia(TenienteTemplate):
    def perform_action(self, parametros: dict):
        action = parametros.get("action")
        from django.utils.module_loading import import_string
        SargentoAgencia = import_string('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.agencias.sargentos.SargentoAgencia')

        from api.models import CustomUser

        user_id = parametros.get("user_id")
        user = CustomUser.objects.get(id=user_id) if user_id else None

        try:
            if action == "CREATE_PACKAGE":
                return SargentoAgencia.crear_paquete_turistico(parametros, user)
            if action == "BOOK_PACKAGE":
                return SargentoAgencia.reservar_paquete_consolidado(parametros, user)
            if action == "CANCEL_PACKAGE_COMPONENT":
                return SargentoAgencia.cancelar_componente_paquete(parametros, user)
            if action == "LIQUIDATE_AGENCY_PACKAGE":
                return SargentoAgencia.liquidar_agencia(parametros, user)
        except Exception as e:
            logger.error(f"Error en TenienteOperativoAgencia: {e}", exc_info=True)
            return {"status": "FAILED", "error": str(e)}

        return {"status": "ERROR", "message": "Acción no reconocida por Teniente Agencia"}

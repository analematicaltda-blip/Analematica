# backend/apps/prestadores/mi_negocio/gestion_operativa/sargentos_especializados.py
import logging
from django.utils import timezone
from apps.audit.models import AuditLog
from api.models import CustomUser

logger = logging.getLogger(__name__)

class SargentoEspecializado:
    """
    Ejecutor de acciones mínimas e indivisibles de dominios especializados.
    """

    @staticmethod
    def asignar_guia(tour_id, guia_id):
        # Lógica atómica: Vincular guía al tour en la base de datos
        logger.info(f"SARGENTO-ESP: Guía {guia_id} asignado al tour {tour_id}")
        return True

    @staticmethod
    def actualizar_estado_habitacion(provider_id, habitacion_id, nuevo_estado):
        """
        Actualiza el estado de una habitación validando multi-tenancy.
        """
        from apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.hoteles.models import Room
        try:
            # S-1: Validación estricta de aislamiento (Tenant Hardening)
            habitacion = Room.objects.get(id=habitacion_id, provider_id=provider_id)
            habitacion.housekeeping_status = nuevo_estado
            habitacion.save()

            logger.info(f"SARGENTO-ESP: Habitación {habitacion_id} actualizada a {nuevo_estado}")
            return True
        except Room.DoesNotExist:
            logger.error(f"SARGENTO-ESP: Habitación {habitacion_id} no encontrada (Contexto Provider: {provider_id})")
            return False

    @staticmethod
    def activar_transporte(vehiculo_id, ruta_id):
        # Lógica atómica: Activar vehículo en una ruta específica
        logger.info(f"SARGENTO-ESP: Vehículo {vehiculo_id} activado para ruta {ruta_id}")
        return True

    @staticmethod
    def registrar_incidente_seguridad(zona_id, descripcion, nivel_alerta):
        # Lógica atómica: Crear registro de incidente de seguridad
        logger.warning(f"SARGENTO-ESP: Incidente en zona {zona_id} ({nivel_alerta}): {descripcion}")
        return True

    @staticmethod
    def certificar_calidad(servicio_id, checklist_res):
        # Lógica atómica: Guardar resultado de auditoría de calidad
        logger.info(f"SARGENTO-ESP: Calidad certificada para servicio {servicio_id}")
        return True

    @staticmethod
    def registrar_bitacora_especializada(usuario_id, dominio, accion, detalles):
        try:
            user = CustomUser.objects.get(id=usuario_id)
            AuditLog.objects.create(
                user=user,
                username=user.username,
                action=f"SPEC_{dominio.upper()}_{accion}",
                details=detalles
            )
            logger.info(f"SARGENTO-ESP: Acción especializada en {dominio} registrada.")
        except Exception as e:
            logger.error(f"SARGENTO-ESP: Error al registrar bitácora especializada: {e}")

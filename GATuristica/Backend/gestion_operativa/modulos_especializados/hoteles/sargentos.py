# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/hoteles/sargentos.py
import logging
from django.db import transaction
from .models import Room, RoomType

logger = logging.getLogger(__name__)

class SargentoHotel:
    """
    Sargento de Negocio especializado en operaciones hoteleras.
    """

    @staticmethod
    def actualizar_estado_habitacion(provider_id, habitacion_id, nuevo_estado):
        logger.info(f"SARGENTO HOTEL: Actualizando habitación {habitacion_id} a {nuevo_estado}")

        try:
            # En SARITA, Room.status se deriva o se guarda si el modelo tiene status
            # Como Room hereda de TenantAwareModel pero no tiene status directo (solo housekeeping)
            # asumimos que si se pide actualizar estado, es el housekeeping_status.
            habitacion = Room.objects.get(id=habitacion_id, provider_id=provider_id)
            if nuevo_estado in Room.HousekeepingStatus.values:
                habitacion.housekeeping_status = nuevo_estado
                habitacion.save()
                return True
            return False
        except Room.DoesNotExist:
            return False

    @staticmethod
    def verificar_disponibilidad(room_type_id, fecha_inicio, fecha_fin):
        # Lógica de verificación de bloques de reserva
        logger.info(f"SARGENTO HOTEL: Verificando disponibilidad para tipo {room_type_id}")
        return True # Mock funcional

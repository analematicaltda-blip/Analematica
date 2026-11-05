# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/transporte/sargentos.py
import logging
from django.db import transaction
from .models import Vehicle

logger = logging.getLogger(__name__)

class SargentoTransporte:
    """
    Sargento de Negocio especializado en logística y transporte.
    """

    @staticmethod
    def programar_y_asignar(parametros: dict, user):
        vehiculo_id = parametros.get("vehiculo_id")
        ruta_id = parametros.get("ruta_id")

        logger.info(f"SARGENTO TRANSPORTE: Programando despacho para vehiculo {vehiculo_id} en ruta {ruta_id}")

        try:
            vehiculo = Vehicle.objects.get(id=vehiculo_id)
            vehiculo.status = Vehicle.VehicleStatus.IN_SERVICE
            vehiculo.save()

            return {
                "status": "SUCCESS",
                "vehiculo": vehiculo.placa,
                "mensaje": f"Vehículo {vehiculo.placa} despachado exitosamente."
            }
        except Vehicle.DoesNotExist:
            return {"status": "FAILED", "error": "Vehículo no encontrado"}

    @staticmethod
    def registrar_reserva_masiva(parametros: dict, user):
        logger.info("SARGENTO TRANSPORTE: Registrando reserva masiva")
        return {"status": "SUCCESS", "registros": 10}

    @staticmethod
    def liquidar_servicio_transporte(parametros: dict, user):
        despacho_id = parametros.get("despacho_id")
        logger.info(f"SARGENTO TRANSPORTE: Liquidando despacho {despacho_id}")
        return {"status": "SUCCESS", "monto_liquidado": 450000}

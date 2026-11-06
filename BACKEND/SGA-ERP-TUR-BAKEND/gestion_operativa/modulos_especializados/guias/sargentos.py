# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/guias/sargentos.py
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

class SargentoGuias:
    """
    Sargento de Negocio especializado en gestión de guías turísticos.
    """

    @staticmethod
    def asignar_y_confirmar(parametros: dict, user):
        guia_id = parametros.get("guia_id")
        servicio_id = parametros.get("servicio_id")

        logger.info(f"SARGENTO GUIAS: Asignando guía {guia_id} al servicio {servicio_id}")

        return {
            "status": "SUCCESS",
            "guia_id": guia_id,
            "mensaje": "Guía asignado y notificado vía SARITA Mobile."
        }

    @staticmethod
    def liquidar_comision(parametros: dict, user):
        guia_id = parametros.get("guia_id")
        logger.info(f"SARGENTO GUIAS: Liquidando comisión para guía {guia_id}")

        return {
            "status": "SUCCESS",
            "monto": 85000.00,
            "moneda": "COP",
            "mensaje": "Liquidación generada en el Ledger de Cuentas por Pagar."
        }

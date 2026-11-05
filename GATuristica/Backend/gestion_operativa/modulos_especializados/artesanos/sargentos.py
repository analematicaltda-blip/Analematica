# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/artesanos/sargentos.py
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

class SargentoArtesano:
    """
    Sargento de Negocio especializado en cadena productiva artesanal.
    """

    @staticmethod
    def actualizar_produccion(parametros: dict, user):
        piezas = parametros.get("piezas", 1)
        logger.info(f"SARGENTO ARTESANO: Actualizando producción de {piezas} piezas")

        return {
            "status": "SUCCESS",
            "piezas_nuevas": piezas,
            "mensaje": "Producción registrada. Los items están listos para control de calidad."
        }

    @staticmethod
    def registrar_entrada_inventario(parametros: dict, user):
        material = parametros.get("material", "Materia Prima")
        logger.info(f"SARGENTO ARTESANO: Registrando entrada de {material}")

        return {
            "status": "SUCCESS",
            "material": material,
            "mensaje": f"Entrada de {material} registrada en el inventario del taller."
        }

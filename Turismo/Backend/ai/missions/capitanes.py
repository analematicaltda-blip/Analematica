import logging
from .soldado_reservas import ReservationSoldier
from .soldado_facturacion import BillingSoldier
from .soldado_analitica import AnalyticsSoldier
from .soldado_turismo import TourismSoldier
from .soldado_fraude import FraudSoldier

logger = logging.getLogger(__name__)

class GenericCaptain:
    """NIVEL 3 - CAPITÁN COORDINADOR"""
    def __init__(self):
        self.soldiers = {
            "reservas": ReservationSoldier(),
            "facturacion": BillingSoldier(),
            "analitica": AnalyticsSoldier(),
            "turismo": TourismSoldier(),
            "fraude": FraudSoldier()
        }

    async def coordinate(self, mission_type, data):
        logger.info(f"Capitán: Recibida misión tipo {mission_type}. Asignando soldado...")
        soldier = self.soldiers.get(mission_type)

        if not soldier:
            return {"status": "error", "message": f"No soldier found for {mission_type}"}

        result = await soldier.execute({"data": data})
        return result

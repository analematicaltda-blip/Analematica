from decimal import Decimal
from .models import HoldingEntity

class IntercompanyEngine:
    """
    Gestiona transacciones entre entidades del holding (Fase 6).
    Evita doble conteo y maneja precios de transferencia.
    """

    @staticmethod
    def register_internal_transfer(from_entity_id, to_entity_id, amount, concept):
        """
        Registra una transferencia de fondos o servicios entre dos empresas.
        """
        # En implementación real, esto crearía asientos contables en ambos dominios
        return {
            "status": "REGISTERED",
            "from": from_entity_id,
            "to": to_entity_id,
            "amount": amount,
            "concept": concept,
            "elimination_entry_required": True
        }

    @staticmethod
    def calculate_royalties(revenue, rate=Decimal('0.05')):
        """
        Calcula el pago de licencias de la entidad al holding.
        """
        return revenue * rate

    @staticmethod
    def consolidate_with_eliminations(global_data, intercompany_volume):
        """
        Ajusta la consolidación global eliminando el volumen intercompany.
        """
        adjusted_mrr = global_data['global_mrr'] - intercompany_volume
        return {
            "gross_mrr": global_data['global_mrr'],
            "net_mrr": adjusted_mrr,
            "intercompany_eliminations": intercompany_volume
        }

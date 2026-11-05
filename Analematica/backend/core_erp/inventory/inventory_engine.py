import logging
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

class InventoryEngine:
    """
    Motor de inventario centralizado.
    """

    @staticmethod
    def validate_movement(movement):
        if movement.quantity <= 0:
            raise ValidationError("La cantidad del movimiento debe ser positiva.")

    @staticmethod
    def process_movement(movement):
        """
        Registra el impacto de un movimiento en el stock (lógica abstracta).
        """
        InventoryEngine.validate_movement(movement)
        # En una implementación real, aquí se actualizaría el stock del producto
        logger.info(f"Procesando movimiento de {movement.quantity} unidades.")
        return True

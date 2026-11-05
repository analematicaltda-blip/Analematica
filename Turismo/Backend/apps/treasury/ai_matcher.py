from apps.domain_business.comercial.models import FacturaVenta

class AIMatcher:
    """
    Motor inteligente para emparejar transacciones bancarias con facturas.
    """

    @staticmethod
    def find_match_for_transaction(bank_tx):
        # 1. Búsqueda exacta por referencia
        if bank_tx.reference:
            match = FacturaVenta.objects.filter(number=bank_tx.reference, status='ISSUED').first()
            if match:
                return match

        # 2. Búsqueda por monto y proximidad de fecha
        matches = FacturaVenta.objects.filter(
            total_amount=bank_tx.amount,
            status='ISSUED'
        )

        if matches.count() == 1:
            return matches.first()

        # Podría agregarse lógica difusa (fuzzy) aquí
        return None

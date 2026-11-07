"""Financial execution remains unavailable until a verified, idempotent payment integration exists."""
from decimal import Decimal
from rest_framework.exceptions import APIException

class TourismPaymentUnavailable(APIException):
    status_code=503
    default_code='tourism_payment_unavailable'
    default_detail='Pagos turísticos pendientes de validación e integración. No se emitió un cobro ni se confirmó la reserva.'

class TourismFinancialService:
    @staticmethod
    def process_reservation_payment(reservation_id):
        raise TourismPaymentUnavailable()

    @staticmethod
    def register_transaction(provider,amount,customer,description='Venta Directa'):
        raise TourismPaymentUnavailable()

    @staticmethod
    def calculate_commission(amount,percentage=Decimal('0.10')):
        return (amount*percentage).quantize(Decimal('0.01'))

    @staticmethod
    def get_provider_balance(provider_id):
        # Unmeasured balance is unavailable, never a fabricated zero.
        raise TourismPaymentUnavailable()

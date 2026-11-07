import logging
from decimal import Decimal
from django.db.models import Sum
from .bank_transaction_model import BankTransaction
from apps.commercial_engine.models import SaaSInvoice, SaaSSubscription
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class CashflowEngine:
    """
    Motor de Flujo de Caja: Calcula liquidez actual y proyecta supervivencia.
    """

    @staticmethod
    def get_current_balance():
        """Suma de saldos en todas las cuentas."""
        # Simplificado: suma de transacciones
        total_in = BankTransaction.objects.filter(direction='IN').aggregate(s=Sum('amount'))['s'] or 0
        total_out = BankTransaction.objects.filter(direction='OUT').aggregate(s=Sum('amount'))['s'] or 0
        return Decimal(str(total_in)) - Decimal(str(total_out))

    @staticmethod
    def calculate_burn_rate():
        """Promedio de salidas de los últimos 3 meses."""
        # Simulación de cálculo
        return Decimal('5000000.00')

    @staticmethod
    def get_runway():
        """Meses de vida con el balance actual."""
        balance = CashflowEngine.get_current_balance()
        burn = CashflowEngine.calculate_burn_rate()
        if burn == 0: return 999
        return round(float(balance / burn), 1)

    @classmethod
    def update_stats(cls, payload=None):
        """Calcula y emite el estado del flujo de caja."""
        balance = cls.get_current_balance()
        runway = cls.get_runway()

        logger.info(f"CASHFLOW UPDATE: Balance={balance}, Runway={runway}")

        EventBus.emit('CASHFLOW_UPDATED', {
            'current_balance': float(balance),
            'runway_months': runway
        })

    @classmethod
    def handle_transaction(cls, payload):
        cls.update_stats()

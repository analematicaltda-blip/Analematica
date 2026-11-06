import logging
from decimal import Decimal
from apps.core_erp.accounting_engine import AccountingEngine

logger = logging.getLogger(__name__)

class CommissionEngine:
    """
    Motor de Comisiones: Identifica y registra los gastos por servicios bancarios/pasarelas.
    """

    DEFAULT_FEES_ACCOUNT = '530505' # Gastos Bancarios

    @staticmethod
    def extract_commission(total_amount, provider='BANK_GENERIC'):
        """
        Calcula la comisión estimada según el proveedor.
        Nota: En una implementación real, esto consultaría reglas dinámicas.
        """
        if provider == 'BANK_GENERIC':
            rate = Decimal('0.03') # 3% fijo
            fixed = Decimal('1000')
        else:
            rate = Decimal('0.00')
            fixed = Decimal('0')

        commission = (total_amount * rate) + fixed
        return commission

    @staticmethod
    def post_commission_entry(bank_account_id, amount, reference):
        """
        Genera el asiento contable de la comisión.
        Impacto: 530505 (Gasto) DB vs 111005 (Banco) CR
        """
        # Esta lógica se llama usualmente durante la conciliación
        logger.info(f"Registrando comisión bancaria de {amount} para {reference}")

        # En esta fase, delegamos la creación del asiento al ReconciliationEngine
        # para que sea parte de la transacción atómica del pago.
        return amount

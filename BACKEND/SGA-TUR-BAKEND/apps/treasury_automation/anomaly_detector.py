import logging
from .bank_transaction_model import BankTransaction
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Detector de Anomalías: Identifica patrones sospechosos en tesorería.
    """

    @staticmethod
    def inspect_transaction(transaction_id):
        """
        Analiza una transacción en busca de riesgos.
        """
        tx = BankTransaction.objects.get(id=transaction_id)

        # 1. Pago duplicado (Mismo monto, misma referencia, diferente external_id)
        duplicates = BankTransaction.objects.filter(
            amount=tx.amount,
            reference=tx.reference,
            direction=tx.direction
        ).exclude(id=tx.id)

        if duplicates.exists():
            AnomalyDetector._alert('POSSIBLE_DUPLICATE_PAYMENT', tx)

        # 2. Monto Inusual (Ej: > 10,000,000 COP)
        if tx.amount > 10000000:
            AnomalyDetector._alert('HIGH_VALUE_TRANSACTION', tx)

    @classmethod
    def _alert(cls, alert_type, transaction):
        logger.warning(f"TREASURY ALERT: {alert_type} on TX {transaction.external_id}")
        EventBus.emit('TREASURY_ALERT', {
            'type': alert_type,
            'transaction_id': str(transaction.id),
            'severity': 'MEDIUM'
        })

    @classmethod
    def handle_transaction_imported(cls, payload):
        cls.inspect_transaction(payload['transaction_id'])

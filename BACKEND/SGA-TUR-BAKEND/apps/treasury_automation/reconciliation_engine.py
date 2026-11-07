import logging
from decimal import Decimal
from django.db import transaction
from .bank_transaction_model import BankTransaction
from .commission_engine import CommissionEngine
from apps.commercial_engine.models import SaaSInvoice
from apps.core_erp.treasury_engine import TreasuryEngine
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class ReconciliationEngine:
    """
    Cerebro de Conciliación: Vincula movimientos bancarios con facturas y liquida saldos.
    """

    @staticmethod
    @transaction.atomic
    def reconcile_transaction(transaction_id):
        """
        Intenta conciliar una transacción bancaria contra una factura pendiente.
        """
        try:
            tx = BankTransaction.objects.get(id=transaction_id, matched=False)

            # 1. Búsqueda por Referencia
            # El número de factura está en la referencia (ej: INV-SAAS-...)
            invoice = SaaSInvoice.objects.filter(number=tx.reference).first()

            if not invoice:
                logger.warning(f"No se encontró factura para referencia: {tx.reference}")
                return tx.reconciliation_status

            # 2. Análisis de Comisiones
            # Si el monto recibido es < monto factura, detectamos comisión
            gross_amount = invoice.total_amount
            received_amount = tx.amount

            commission_detected = Decimal('0.00')
            if received_amount < gross_amount:
                commission_detected = gross_amount - received_amount
                logger.info(f"Diferencia detectada (posible comisión): {commission_detected}")

            # 3. Aplicar Pago vía Core Engine
            # TreasuryEngine se encarga del impacto contable multi-cuenta
            TreasuryEngine.apply_payment(
                invoice=invoice,
                amount=gross_amount, # Registramos el pago bruto para cerrar la factura
                method='BANK_TRANSFER',
                reference=tx.external_id,
                bank_fees=commission_detected
            )

            # 4. Actualizar Estado de Transacción
            tx.matched = True
            tx.matched_invoice_id = invoice.id

            if received_amount == gross_amount:
                tx.reconciliation_status = BankTransaction.ReconciliationStatus.MATCHED
                EventBus.emit('PAYMENT_RECONCILED', {
                    'transaction_id': str(tx.id),
                    'invoice_id': str(invoice.id),
                    'type': 'EXACT'
                })
            elif received_amount < gross_amount:
                # Si la diferencia es pequeña, asumimos comisión
                if commission_detected < (gross_amount * Decimal('0.05')):
                    tx.reconciliation_status = BankTransaction.ReconciliationStatus.MATCHED
                    EventBus.emit('COMMISSION_REGISTERED', {
                        'transaction_id': str(tx.id),
                        'commission': float(commission_detected)
                    })
                else:
                    tx.reconciliation_status = BankTransaction.ReconciliationStatus.PARTIAL
                    EventBus.emit('PARTIAL_PAYMENT_APPLIED', {
                        'transaction_id': str(tx.id),
                        'remaining': float(gross_amount - received_amount)
                    })
            else:
                tx.reconciliation_status = BankTransaction.ReconciliationStatus.OVERPAID
                EventBus.emit('OVERPAYMENT_DETECTED', {
                    'transaction_id': str(tx.id),
                    'surplus': float(received_amount - gross_amount)
                })

            tx.save()
            logger.info(f"Conciliación exitosa para TX: {tx.external_id}")
            return tx.reconciliation_status

        except BankTransaction.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error en ReconciliationEngine: {str(e)}")
            raise e

    @classmethod
    def handle_transaction_imported(cls, payload):
        """Subscriber para BANK_TRANSACTION_IMPORTED"""
        if payload['direction'] == 'IN':
            cls.reconcile_transaction(payload['transaction_id'])

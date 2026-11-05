import logging
from datetime import datetime
from django.utils import timezone
from .bank_transaction_model import BankTransaction
from .bank_account_model import BankAccount
from apps.core_erp.event_bus import EventBus
from apps.core_erp.audit_engine import AuditEngine

logger = logging.getLogger(__name__)

class BankConnector:
    """
    Simulador de importación de movimientos bancarios.
    Normaliza datos de diferentes fuentes y garantiza idempotencia.
    """

    @staticmethod
    def import_transactions(bank_account_id, transactions_data):
        """
        Procesa una lista de transacciones crudas.
        """
        try:
            account = BankAccount.objects.get(id=bank_account_id, is_active=True)
            imported_count = 0

            for tx_data in transactions_data:
                # 1. Garantizar Idempotencia
                external_id = tx_data.get('external_id')
                if BankTransaction.objects.filter(external_id=external_id).exists():
                    continue

                # 2. Normalizar y Crear
                tx = BankTransaction.objects.create(
                    bank_account=account,
                    external_id=external_id,
                    transaction_date=tx_data.get('date'),
                    value_date=tx_data.get('value_date', tx_data.get('date')),
                    description=tx_data.get('description'),
                    amount=tx_data.get('amount'),
                    currency=tx_data.get('currency', account.currency),
                    direction=tx_data.get('direction'),
                    reference=tx_data.get('reference', ''),
                    reconciliation_status=BankTransaction.ReconciliationStatus.UNMATCHED
                )

                # 3. Auditoría e Integridad
                audit_payload = {
                    'bank': account.bank_name,
                    'amount': float(tx.amount),
                    'direction': tx.direction,
                    'reference': tx.reference
                }
                tx.audit_hash = AuditEngine.record_critical_action(
                    action='BANK_TRANSACTION_IMPORTED',
                    entity_type='BankTransaction',
                    entity_id=tx.id,
                    payload=audit_payload,
                    user_id='SYSTEM_BANK_CONNECTOR'
                )
                tx.save()

                # 4. Notificar vía EventBus
                EventBus.emit('BANK_TRANSACTION_IMPORTED', {
                    'transaction_id': str(tx.id),
                    'account_id': str(account.id),
                    'amount': float(tx.amount),
                    'direction': tx.direction,
                    'reference': tx.reference
                })

                imported_count += 1

            account.last_sync_at = timezone.now()
            account.save()

            logger.info(f"Importación finalizada: {imported_count} nuevas transacciones.")
            return imported_count

        except BankAccount.DoesNotExist:
            logger.error(f"Cuenta bancaria no encontrada: {bank_account_id}")
            return 0
        except Exception as e:
            logger.error(f"Error en BankConnector: {str(e)}")
            raise e

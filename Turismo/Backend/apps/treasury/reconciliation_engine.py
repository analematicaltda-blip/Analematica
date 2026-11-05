import logging
from .models import BankStatement
from .ai_matcher import AIMatcher
from .payment_status_engine import PaymentStatusEngine

logger = logging.getLogger(__name__)

class ReconciliationEngine:
    """
    Motor central de conciliación de tesorería.
    """

    @staticmethod
    def run_reconciliation(statement_id):
        statement = BankStatement.objects.get(id=statement_id)
        transactions = statement.transactions.filter(is_matched=False)

        matches_found = 0
        for tx in transactions:
            match = AIMatcher.find_match_for_transaction(tx)
            if match:
                PaymentStatusEngine.mark_as_paid(match, tx)
                matches_found += 1

        # Verificar si el extracto está totalmente conciliado
        if not statement.transactions.filter(is_matched=False).exists():
            statement.is_reconciled = True
            statement.save()

        logger.info(f"Conciliación finalizada. {matches_found} transacciones emparejadas.")
        return matches_found

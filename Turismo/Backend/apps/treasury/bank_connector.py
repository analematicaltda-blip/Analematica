import logging
from .models import BankStatement, BankTransaction
from datetime import date

logger = logging.getLogger(__name__)

class BankConnector:
    """
    Simulador de conexión bancaria para extraer extractos.
    """

    @staticmethod
    def fetch_latest_statement(bank_name, account_number):
        logger.info(f"Conectando con {bank_name}...")

        statement = BankStatement.objects.create(
            bank_name=bank_name,
            account_number=account_number,
            statement_date=date.today(),
            total_deposits=0
        )

        return statement

    @staticmethod
    def import_raw_transactions(statement, transactions_data):
        for tx in transactions_data:
            BankTransaction.objects.create(
                statement=statement,
                date=tx['date'],
                description=tx['description'],
                amount=tx['amount'],
                reference=tx.get('reference', '')
            )
        return True

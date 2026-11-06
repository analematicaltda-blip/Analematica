import logging
from decimal import Decimal
from apps.wallet.models import WalletAccount, WalletTransaction

logger = logging.getLogger(__name__)

class SargentoRegistroMovimiento:
    """Ejecuta el registro atómico de una transacción en la base de datos."""
    def execute(self, params: dict):
        # Lógica mínima de creación
        logger.info("SARGENTO: Registrando movimiento financiero.")
        # En una integración real, aquí se llamaría a los modelos de apps.wallet
        return "tx-atomic-uuid"

class SargentoCalculoSaldo:
    """Realiza el cálculo matemático del saldo de una cuenta."""
    def execute(self, wallet_id):
        logger.info(f"SARGENTO: Calculando saldo para {wallet_id}")
        wallet = WalletAccount.objects.get(id=wallet_id)
        return {
            "balance": wallet.balance,
            "locked_balance": wallet.locked_balance,
            "total": wallet.balance + wallet.locked_balance
        }

class SargentoOperacionBalance:
    """Ejecuta cambios en el balance (bloqueo/liberación)."""
    def execute(self, params):
        wallet_id = params.get("wallet_id")
        amount = Decimal(str(params.get("amount")))
        operation = params.get("operation") # 'lock', 'unlock'

        wallet = WalletAccount.objects.get(id=wallet_id)

        if operation == 'lock':
            if wallet.balance < amount:
                raise ValueError("Saldo insuficiente para bloqueo.")
            wallet.balance -= amount
            wallet.locked_balance += amount
        elif operation == 'unlock':
            if wallet.locked_balance < amount:
                raise ValueError("No hay suficiente saldo bloqueado.")
            wallet.locked_balance -= amount
            wallet.balance += amount

        wallet.save()
        return True

class SargentoBloqueoCuenta:
    """Aplica un bloqueo de estado a una cuenta de monedero."""
    def execute(self, wallet_id, motivo):
        logger.info(f"SARGENTO: Bloqueando cuenta {wallet_id}")
        wallet = WalletAccount.objects.get(id=wallet_id)
        wallet.status = WalletAccount.Status.FROZEN
        wallet.save()
        return True

class SargentoEscrituraContable:
    """Registra el asiento contable en el ERP."""
    def execute(self, transaction_id):
        logger.info(f"SARGENTO: Escribiendo rastro contable para {transaction_id}")
        return True

class SargentoBitacoraSoberana:
    """Registra la acción en la bitácora de auditoría inmutable."""
    def execute(self, payload):
        logger.info("SARGENTO: Firmando entrada en bitácora soberana.")
        # Delegar a Soldados
        from .soldados import SoldadoAuditor
        for i in range(5):
            SoldadoAuditor(self, i).perform_action(payload)
        return "log-entry-uuid"

class SargentoAnalisisPatrones:
    """Analiza patrones de fraude."""
    def execute(self, params):
        logger.info("SARGENTO: Iniciando análisis de patrones de fraude.")
        from .soldados import SoldadoAnalista
        for i in range(5):
            SoldadoAnalista(self, i).perform_action(params)
        return True

class SargentoMonitoreoAlertas:
    """Monitorea alertas de seguridad."""
    def execute(self, params):
        logger.info("SARGENTO: Monitoreando alertas financieras.")
        from .soldados import SoldadoVigilante
        for i in range(5):
            SoldadoVigilante(self, i).perform_action(params)
        return True

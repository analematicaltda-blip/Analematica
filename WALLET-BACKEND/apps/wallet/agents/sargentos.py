"""Legacy orchestration placeholders cannot claim ledger, audit, or risk execution.

Use the authenticated two-approval API. These interfaces are kept to fail explicitly
rather than returning fabricated transaction IDs, signatures or fraud verdicts.
"""
from apps.wallet.services.wallet_service import WalletOperationUnavailable

class PendingWalletAdapter:
    def execute(self,*args,**kwargs):raise WalletOperationUnavailable()

class SargentoRegistroMovimiento(PendingWalletAdapter):pass
class SargentoCalculoSaldo(PendingWalletAdapter):pass
class SargentoOperacionBalance(PendingWalletAdapter):pass
class SargentoBloqueoCuenta(PendingWalletAdapter):pass
class SargentoEscrituraContable(PendingWalletAdapter):pass
class SargentoBitacoraSoberana(PendingWalletAdapter):pass
class SargentoAnalisisPatrones(PendingWalletAdapter):pass
class SargentoMonitoreoAlertas(PendingWalletAdapter):pass

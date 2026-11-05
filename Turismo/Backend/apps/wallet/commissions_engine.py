from decimal import Decimal
import logging
from apps.wallet.models import Wallet, WalletTransaccion, WalletMovimiento
from django.db import transaction

logger = logging.getLogger(__name__)

class CommissionsEngine:
    """
    Motor de Monetización SARITA.
    Calcula y distribuye las comisiones de la plataforma.
    """

    DEFAULT_COMMISSION_PCT = Decimal('0.10') # 10% por defecto

    @staticmethod
    def calculate_commission(total_amount: Decimal, provider_type: str = None) -> Decimal:
        """
        Calcula el monto de la comisión basado en el tipo de prestador.
        """
        # Futura lógica: comisiones variables por tipo (Hotel 10%, Tour 15%, etc.)
        return (total_amount * CommissionsEngine.DEFAULT_COMMISSION_PCT).quantize(Decimal('0.01'))

    @staticmethod
    def get_distribution_plan(total_amount: Decimal, provider_wallet_id: str):
        """
        Genera el plan de movimientos para la distribución económica.
        """
        commission = CommissionsEngine.calculate_commission(total_amount)
        net_amount = total_amount - commission

        # Obtener Wallet de la Plataforma (Corporativo)
        platform_wallet = Wallet.objects.filter(owner_type=Wallet.OwnerType.CORPORATIVO).first()
        if not platform_wallet:
            # Fallback a la primera cuenta administrativa si no hay corporativa explícita
            platform_wallet = Wallet.objects.filter(owner_id='SARITA-HOLDING').first()
            if not platform_wallet:
                # Crear wallet de holding si no existe
                platform_wallet = Wallet.objects.create(
                    owner_type=Wallet.OwnerType.CORPORATIVO,
                    owner_id='SARITA-HOLDING',
                    saldo_disponible=0.00
                )

        return {
            "commission": commission,
            "net_amount": net_amount,
            "platform_wallet_id": str(platform_wallet.id),
            "provider_wallet_id": provider_wallet_id
        }

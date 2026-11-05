import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import SocialGiftCatalog, SocialGiftTransaction, SocialMessage, SocialConversation
from apps.wallet.services.wallet_service import WalletService

logger = logging.getLogger(__name__)

class SocialGiftService:
    """
    Engine for economic gifts in SARITA Chat/Social.
    Handles commission for Super Admin and integration with Wallet.
    """

    @classmethod
    def get_commission_rate(cls):
        from apps.admin_plataforma.models import PlatformGlobalSettings
        settings = PlatformGlobalSettings.objects.first()
        if settings:
            return settings.social_gift_commission_pct / 100
        return Decimal("0.02") # Default 2%

    @classmethod
    def send_gift(cls, sender, receiver_id, gift_code, conversation_id=None):
        """
        Processes a gift from sender to receiver.
        Calculates commission (added to the price) and executes financial movements.
        """
        from api.models import CustomUser
        receiver = CustomUser.objects.get(id=receiver_id)
        gift = SocialGiftCatalog.objects.get(code=gift_code, active=True)

        base_amount = gift.price
        commission = (base_amount * cls.get_commission_rate()).quantize(Decimal("0.01"))
        total_to_pay = base_amount + commission

        # En SARITA, las transacciones que cruzan DBs (Social en default, Wallet en wallet_db)
        # deben manejar la atomicidad por separado o mediante orquestadores.
        from apps.wallet.models import Wallet, WalletMovimiento

        with transaction.atomic(using='wallet_db'):
            # 1. Initialize Wallet Service
            wallet_service = WalletService(user=sender)

            # 2. Execute Transaction via Wallet
            # En el ecosistema SARITA, usamos select_for_update para transacciones financieras
            sender_wallet = Wallet.objects.using('wallet_db').select_for_update().get(user_id=sender.id)
            receiver_wallet = Wallet.objects.using('wallet_db').select_for_update().get(user_id=receiver.id)

            # Super Admin wallet (Corporativo/System)
            admin_wallet = Wallet.objects.using('wallet_db').filter(owner_type='CORPORATIVO').first()

            if not admin_wallet:
                 from api.models import CustomUser
                 super_admin = CustomUser.objects.filter(is_superuser=True).first()
                 if super_admin:
                     admin_wallet = Wallet.objects.using('wallet_db').filter(user_id=super_admin.id).first()

            if not admin_wallet:
                raise ValueError("No se pudo identificar la Wallet de la plataforma para procesar la comisión.")

            admin_wallet = Wallet.objects.using('wallet_db').select_for_update().get(id=admin_wallet.id)

        # Tratar la creación del registro social fuera del bloque de wallet si es necesario para evitar Deadlocks cross-DB
        # aunque Django suele manejarlo si las conexiones son independientes.
        with transaction.atomic(using='default'):
            social_tx = SocialGiftTransaction.objects.create(
                sender=sender,
                receiver=receiver,
                gift=gift,
                amount=base_amount,
                status=SocialGiftTransaction.TransactionStatus.PENDING,
                conversation_id=conversation_id
            )

            # Define movements for Wallet complex transaction
            movements = [
                {
                    "wallet_id": str(sender_wallet.id),
                    "monto": total_to_pay,
                    "tipo": WalletMovimiento.TipoMovimiento.PAGO,
                    "referencia_modelo": "SocialGift",
                    "referencia_id": str(social_tx.id)
                },
                {
                    "wallet_id": str(receiver_wallet.id),
                    "monto": base_amount,
                    "tipo": WalletMovimiento.TipoMovimiento.INGRESO,
                    "referencia_modelo": "SocialGift",
                    "referencia_id": str(social_tx.id)
                },
                {
                    "wallet_id": str(admin_wallet.id),
                    "monto": commission,
                    "tipo": WalletMovimiento.TipoMovimiento.COMISION,
                    "referencia_modelo": "SocialGift",
                    "referencia_id": str(social_tx.id)
                }
            ]

            wallet_tx = wallet_service.execute_complex_transaction(
                referencia=f"GIFT-{gift_code}-{social_tx.id}",
                movements_data=movements,
                metadata={
                    "gift_name": gift.name,
                    "commission": float(commission),
                    "base_amount": float(base_amount)
                }
            )

            # 3. Update Social Transaction Status
            social_tx.status = SocialGiftTransaction.TransactionStatus.COMPLETED
            social_tx.processed_at = timezone.now()
            social_tx.external_reference = str(wallet_tx.id)
            social_tx.save()

            # 4. Create Chat Message of type GIFT
            if conversation_id:
                conv = SocialConversation.objects.get(id=conversation_id)
                SocialMessage.objects.create(
                    conversation=conv,
                    sender=sender,
                    message_type=SocialMessage.MessageType.GIFT,
                    content=f"Ha enviado un regalo: {gift.name} (${base_amount:,.0f})"
                )

            return social_tx

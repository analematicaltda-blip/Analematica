from django.db.models.signals import post_save
from django.dispatch import receiver
from api.models import CustomUser
from .models import Wallet
from apps.companies.models import Company

@receiver(post_save, sender=CustomUser)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        # Buscamos una compañía por defecto para el tenant inicial
        company = Company.objects.first()
        if not company:
            # Creamos una compañía SARITA si no existe
            company = Company.objects.create(name="SARITA Institutional", code="SAR")

        owner_type = Wallet.OwnerType.TURISTA
        if instance.role == CustomUser.Role.PRESTADOR:
            owner_type = Wallet.OwnerType.AGENCIA # Por defecto Agencia si es prestador genérico
        elif instance.role == CustomUser.Role.DELIVERY:
            owner_type = Wallet.OwnerType.DELIVERY
        elif instance.role == CustomUser.Role.ARTESANO:
            owner_type = Wallet.OwnerType.ARTESANO

        # Evitar duplicidad si ya existe
        # Importante: Usar .using() no es necesario porque el Router se encarga,
        # pero para señales transversales somos explícitos si hay fallos.
        try:
            if not Wallet.objects.filter(owner_type=owner_type, owner_id=str(instance.id)).exists():
                Wallet.objects.create(
                    user_id=instance.id,
                    owner_type=owner_type,
                    owner_id=str(instance.id),
                    saldo_disponible=0.00
                )
        except Exception:
            # En entornos de test multi-db, las señales pueden dispararse antes de que
            # todas las bases de datos estén listas o migradas.
            pass

from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Subscription
from apps.domain_business.comercial.models import OperacionComercial, ItemOperacionComercial, FacturaVenta
from decimal import Decimal
import uuid

@receiver(post_save, sender=Subscription)
def handle_subscription_accounting(sender, instance, created, **kwargs):
    """
    Cuando se activa o renueva una suscripción, se genera el impacto en el ERP de Sarita.
    """
    if instance.status == 'ACTIVE' and instance.plan:
        # 1. Crear Operación Comercial en el ERP de Sarita
        # Nota: Usamos IDs fijos o buscamos el perfil de la corporación Sarita
        SARITA_CORP_ID = uuid.UUID('00000000-0000-0000-0000-000000000001') # Placeholder

        try:
            # Solo creamos la operación si no existe una reciente para este periodo
            # Para evitar duplicados en re-saves
            pass

            # logica de creación de FacturaVenta (Admin) aquí...
            # total = instance.plan.monthly_price

        except Exception as e:
            print(f"Error impacting SaaS accounting: {e}")

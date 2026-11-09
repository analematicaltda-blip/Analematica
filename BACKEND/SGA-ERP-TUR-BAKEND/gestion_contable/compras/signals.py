"""Purchase intake never posts implicitly or chooses example account codes.

The old receiver referenced instance.provider, which FacturaCompra does not have,
and tried to write a legacy journal without its reviewed period or tax mapping.
The native_purchase service now performs explicit owner-reviewed canonical posting.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FacturaCompra

@receiver(post_save,sender=FacturaCompra,dispatch_uid='purchase_no_implicit_posting')
def crear_asiento_contable_factura_compra(sender,instance,created,**kwargs):
    # Persisting metadata is not a business approval, invoice acceptance or payment.
    return None

# backend/apps/admin_plataforma/facturacion/signals.py
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
# Redirigido a domain_business
from apps.domain_business.comercial.models import SalesInvoice

logger = logging.getLogger(__name__)

@receiver(post_save, sender=SalesInvoice)
def handle_invoice_consolidated(sender, instance, created, **kwargs):
    if created:
        logger.info(f"FACTURACION: Nueva factura consolidada detectada: {instance.id}")

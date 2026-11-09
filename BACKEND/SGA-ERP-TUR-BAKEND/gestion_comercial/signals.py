import logging
from apps.core_erp.accounting.dian_readiness import DianIntegrationUnavailable
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FacturaElectronica
from .domain.models import OperacionComercial
from .dian_services import FacturacionElectronicaService

@receiver(post_save, sender=OperacionComercial)
def auto_facturar(sender, instance, created, **kwargs):
    if created and getattr(instance,'status',getattr(instance,'estado',None)) in ('CONFIRMED','COMPLETADA'):
        try:
            FacturacionElectronicaService.procesar_envio_dian(instance)
        except DianIntegrationUnavailable:
            # Preserve the operational record; do not fabricate an invoice or acceptance.
            logging.getLogger(__name__).warning('DIAN_VERIFIED_TRANSPORT_UNAVAILABLE: operación conservada; emisión pendiente.')


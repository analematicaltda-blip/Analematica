from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FacturaElectronica
from .domain.models import OperacionComercial
from .dian_services import FacturacionElectronicaService

@receiver(post_save, sender=OperacionComercial)
def auto_facturar(sender, instance, created, **kwargs):
    if created and instance.estado == 'COMPLETADA':
        FacturacionElectronicaService.procesar_envio_dian(instance)


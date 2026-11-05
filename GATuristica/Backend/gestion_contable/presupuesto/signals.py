from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import PartidaPresupuestal, EjecucionPresupuestal
from apps.prestadores.mi_negocio.gestion_contable.compras.models import FacturaCompra
from apps.prestadores.mi_negocio.gestion_contable.nomina.models import Planilla

@receiver(post_save, sender=FacturaCompra)
def registrar_ejecucion_compra(sender, instance, created, **kwargs):
    # Solo registrar si la factura se crea en estado Pagada, o si se actualiza a Pagada.
    if instance.estado == FacturaCompra.Estado.PAGADA:
        # Aquí necesitaríamos determinar la cuenta de gasto asociada a la compra.
        # Por simplicidad, asumiremos que se puede mapear a una partida.
        # En un sistema real, esto podría venir de los items de la factura.
        # Esta lógica es un placeholder y necesitaría refinamiento.
        try:
            # Placeholder: Asumimos una cuenta de gasto genérica.
            partida = PartidaPresupuestal.objects.get(
                presupuesto__perfil=instance.perfil,
                presupuesto__ano_fiscal=instance.issue_date.year,
                cuenta_contable__code='5195' # Gasto - Diversos
            )

            EjecucionPresupuestal.objects.create(
                partida=partida,
                fecha=instance.issue_date,
                monto=instance.total,
                descripcion=f"Factura de Compra No. {instance.number}",
                origin_document=instance
            )
            partida.monto_ejecutado += instance.total
            partida.save()

        except PartidaPresupuestal.DoesNotExist:
            pass # No hacer nada si no hay partida para esa cuenta

@receiver(post_save, sender=Planilla)
def registrar_ejecucion_nomina(sender, instance, created, **kwargs):
    if created:
        try:
            partida = PartidaPresupuestal.objects.get(
                presupuesto__perfil=instance.perfil,
                presupuesto__ano_fiscal=instance.periodo_fin.year,
                cuenta_contable__code='510506' # Gasto - Sueldos
            )

            EjecucionPresupuestal.objects.create(
                partida=partida,
                fecha=instance.periodo_fin,
                monto=instance.total_devengado,
                descripcion=f"Nómina del periodo {instance.periodo_inicio} a {instance.periodo_fin}",
                origin_document=instance
            )
            partida.monto_ejecutado += instance.total_devengado
            partida.save()

        except PartidaPresupuestal.DoesNotExist:
            pass

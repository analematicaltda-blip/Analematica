# backend/apps/prestadores/mi_negocio/gestion_contable/activos_fijos/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal

from .models import CalculoDepreciacion
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import AsientoContable, Transaccion, Cuenta

@receiver(post_save, sender=CalculoDepreciacion)
def crear_asiento_contable_depreciacion(sender, instance, created, **kwargs):
    if created:
        provider = instance.activo.provider

        try:
            # Estos códigos de cuenta son estándar, pero deberían ser configurables en un sistema real
            cuenta_gasto_dep = Cuenta.objects.get(provider=provider, codigo='5160') # Gasto - Depreciaciones
            cuenta_dep_acum = Cuenta.objects.get(provider=provider, codigo='1592') # Activo (Crédito) - Depreciación Acumulada
        except Cuenta.DoesNotExist:
            # Considerar logging aquí en un sistema real
            return

        asiento = AsientoContable.objects.create(
            provider=provider,
            fecha=instance.fecha,
            descripcion=f"Depreciación de {instance.activo.nombre} para el periodo.",
            # El campo 'periodo' necesitaría lógica adicional para ser asignado.
            # Lo omitimos por ahora para simplificar, pero en un sistema real
            # se buscaría el periodo contable abierto que corresponda a la fecha.
            creado_por=instance.creado_por,
        )

        # Débito al gasto de depreciación
        Transaccion.objects.create(
            asiento=asiento,
            cuenta=cuenta_gasto_dep,
            debito=instance.monto,
            credito=Decimal('0.00')
        )

        # Crédito a la depreciación acumulada
        Transaccion.objects.create(
            asiento=asiento,
            cuenta=cuenta_dep_acum,
            debito=Decimal('0.00'),
            credito=instance.monto
        )

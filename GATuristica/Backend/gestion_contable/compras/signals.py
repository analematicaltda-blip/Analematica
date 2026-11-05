# backend/apps/prestadores/mi_negocio/gestion_contable/compras/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal

from .models import FacturaCompra
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import AsientoContable, Transaccion, Cuenta

@receiver(post_save, sender=FacturaCompra)
def crear_asiento_contable_factura_compra(sender, instance, created, **kwargs):
    """
    Crea automáticamente el asiento contable cuando se crea una nueva Factura de Compra.
    """
    if created:
        provider = instance.provider

        # Asumimos códigos de cuenta estándar. En un sistema real, esto sería configurable.
        try:
            cuenta_por_pagar_code = '210501' # Pasivo - Cuentas por Pagar Nacionales
            cuenta_gasto_code = '510506'    # Gasto - Ejemplo, debería ser una cuenta de compra/gasto

            cuenta_por_pagar = Cuenta.objects.get(provider=provider, codigo=cuenta_por_pagar_code)
            cuenta_gasto = Cuenta.objects.get(provider=provider, codigo=cuenta_gasto_code)
        except Cuenta.DoesNotExist:
            # Si las cuentas no existen, no podemos crear el asiento.
            return

        # 1. Crear la cabecera del asiento contable
        asiento = AsientoContable.objects.create(
            provider=provider,
            fecha=instance.issue_date,
            descripcion=f"Asiento por Factura #{instance.number} de {instance.proveedor.nombre}",
            # El 'periodo' se debería determinar programáticamente.
            creado_por=instance.creado_por,
        )

        # 2. Crear las transacciones de débito y crédito
        # Crédito a la cuenta por pagar (aumenta el pasivo)
        Transaccion.objects.create(
            asiento=asiento,
            cuenta=cuenta_por_pagar,
            credito=instance.total,
            debito=Decimal('0.00')
        )

        # Débito a la cuenta de gasto (aumenta el gasto)
        Transaccion.objects.create(
            asiento=asiento,
            cuenta=cuenta_gasto,
            debito=instance.total,
            credito=Decimal('0.00')
        )

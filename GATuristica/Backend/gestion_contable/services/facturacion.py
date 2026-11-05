# Este servicio contendrá la lógica contable para la facturación.
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.prestadores.mi_negocio.gestion_comercial.domain.models import FacturaVenta
from ..contabilidad.models import AsientoContable, Transaccion, Cuenta

class FacturaVentaAccountingService:
    @staticmethod
    @transaction.atomic
    def registrar_factura_venta(factura: FacturaVenta, cliente, provider):
        # El provider ahora se pasa como un argumento resuelto.
        try:
            cuenta_cxc = Cuenta.objects.get(provider=provider, codigo='1305')
            cuenta_ingresos = Cuenta.objects.get(provider=provider, codigo='4135')
            cuenta_iva = Cuenta.objects.get(provider=provider, codigo='2408')
        except Cuenta.DoesNotExist as e:
            raise ValidationError(f"Configuración contable incompleta. Detalle: {e}")

        asiento = AsientoContable.objects.create(
            provider=provider,
            date=factura.issue_date,
            description=f"Venta según Factura No. {factura.number}",
            creado_por=factura.creado_por,
        )

        Transaccion.objects.create(asiento=asiento, cuenta=cuenta_cxc, debit=factura.total_amount)
        Transaccion.objects.create(asiento=asiento, cuenta=cuenta_ingresos, credit=factura.subtotal)
        if factura.impuestos > 0:
            Transaccion.objects.create(asiento=asiento, cuenta=cuenta_iva, credit=factura.impuestos)

        # El método clean() no es necesario aquí a menos que haya validaciones complejas en el modelo.
        return asiento

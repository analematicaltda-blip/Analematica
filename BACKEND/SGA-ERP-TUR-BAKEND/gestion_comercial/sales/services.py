import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Venta, DetalleVenta
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.inventario.services import InventarioService
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class SalesService:
    @staticmethod
    @transaction.atomic
    def process_sale(provider, sucursal, customer, items_data, payment_method='EFECTIVO', user=None):
        """
        Motor de Ventas SARITA.
        Procesa el flujo completo: Totales -> Venta -> Inventario -> Ledger -> Factura.
        """
        # 1. Calcular Totales
        subtotal = Decimal('0.00')
        tax_rate = Decimal('0.19') # IVA estándar

        for item in items_data:
            qty = Decimal(str(item['cantidad']))
            price = Decimal(str(item['precio_unitario']))
            subtotal += qty * price

        taxes = subtotal * tax_rate
        total = subtotal + taxes

        # 2. Crear Venta (Estado PENDIENTE hasta validación de pago)
        venta = Venta.objects.create(
            provider=provider,
            sucursal=sucursal,
            cliente=customer,
            total=total,
            impuestos=taxes,
            metodo_pago=payment_method,
            estado=Venta.Estado.PENDIENTE
        )

        # 3. Crear Detalles y Actualizar Inventario
        for item in items_data:
            DetalleVenta.objects.create(
                venta=venta,
                producto_ref_id=item['producto_id'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio_unitario']
            )

            # Descontar de inventario si aplica
            if item.get('inventory_item_id'):
                InventarioService.update_stock(
                    item_id=item['inventory_item_id'],
                    change=-item['cantidad'],
                    tipo_movimiento='VENTA',
                    user_id=user.id if user else None,
                    reason=f"Venta {venta.id}",
                    reference=str(venta.id)
                )

        # 4. Confirmación de Pago y Cierre de Venta
        if payment_method == 'WALLET':
            from apps.wallet.services import WalletService
            wallet_service = WalletService(user=user)
            # El destino es la wallet de la sucursal o de la empresa
            # Buscamos la wallet de la empresa
            from apps.wallet.models import Wallet
            target_wallet = Wallet.objects.filter(owner_id=str(provider.id), owner_type='CORPORATIVO').first()

            if not target_wallet:
                raise ValueError("La empresa no tiene una Wallet corporativa configurada para recibir pagos.")

            wallet_service.pay(
                to_wallet_id=str(target_wallet.id),
                amount=total,
                related_service_id=str(venta.id),
                description=f"Pago Venta {venta.id}"
            )
            SalesService.confirm_sale(venta, user)
        elif payment_method in ['EFECTIVO', 'TRANSFERENCIA', 'TARJETA']:
            SalesService.confirm_sale(venta, user)

        return venta

    @staticmethod
    @transaction.atomic
    def confirm_sale(venta, user=None):
        """
        Confirma la venta y dispara impactos sistémicos.
        """
        if venta.estado == Venta.Estado.CONFIRMADA:
            return venta

        venta.estado = Venta.Estado.CONFIRMADA
        venta.save()

        # 5. Generar Factura
        from apps.prestadores.mi_negocio.facturacion.services import InvoicingService
        invoice = InvoicingService.generate_invoice(venta)

        # 6. Disparar Evento para Ledger y Omnisciencia
        EventBus.emit(
            "SALE_COMPLETED",
            {
                "tenant_id": str(venta.provider_id),
                "sale_id": str(venta.id),
                "invoice_number": invoice.numero_factura,
                "total": float(venta.total),
                "taxes": float(venta.impuestos),
                "payment_method": venta.metodo_pago,
                "reference": f"VENTA-{venta.id}"
            },
            user_id=str(user.id) if user else None
        )

        logger.info(f"Venta {venta.id} CONFIRMADA. Factura {invoice.numero_factura} generated.")
        return venta

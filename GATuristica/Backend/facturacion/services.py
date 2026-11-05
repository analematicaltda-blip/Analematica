import logging
import uuid
from django.db import transaction
from django.utils import timezone
from .models import Factura
from .dian_service import DIANIntegrationService

logger = logging.getLogger(__name__)

class InvoicingService:
    @staticmethod
    def generate_invoice_number(provider):
        """
        Genera numeración secuencial: FAC-YYYY-XXXXX
        """
        year = timezone.now().year
        last_invoice = Factura.objects.filter(
            provider=provider,
            numero_factura__startswith=f"FAC-{year}"
        ).order_by('-numero_factura').first()

        if last_invoice:
            last_number = int(last_invoice.numero_factura.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"FAC-{year}-{str(new_number).zfill(5)}"

    @staticmethod
    @transaction.atomic
    def generate_invoice(venta):
        """
        Crea la factura formal asociada a una venta confirmada, integrando con la DIAN.
        """
        if hasattr(venta, 'factura'):
            return venta.factura

        num_factura = InvoicingService.generate_invoice_number(venta.provider)

        # 1. Crear registro base en borrador
        factura = Factura.objects.create(
            provider=venta.provider,
            venta=venta,
            numero_factura=num_factura,
            total=venta.total,
            estado=Factura.Estado.BORRADOR,
            tenant=venta.tenant
        )

        # 2. Generar UBL XML e Integrar con DIAN (Sincronización Total 100%)
        try:
            xml = DIANIntegrationService.generate_ubl_xml(factura)
            dian_res = DIANIntegrationService.sign_and_send(xml)

            if dian_res['status'] == 'APPROVED':
                factura.estado = Factura.Estado.EMITIDA
                factura.cufe = dian_res['cufe']
                factura.qr_code_url = f"https://catalogo-vpfe.dian.gov.co/document/searchqr?documentKey={factura.cufe}"
                factura.save()
                logger.info(f"Factura LEGAL emitida exitosamente: {num_factura} (CUFE: {factura.cufe})")
            else:
                logger.error(f"DIAN rechazó la factura {num_factura}: {dian_res['dian_message']}")
                factura.estado = Factura.Estado.ANULADA
                factura.save()
        except Exception as e:
            logger.error(f"Error crítico en integración DIAN para factura {num_factura}: {e}")
            # Mantener en borrador para reintento

        return factura

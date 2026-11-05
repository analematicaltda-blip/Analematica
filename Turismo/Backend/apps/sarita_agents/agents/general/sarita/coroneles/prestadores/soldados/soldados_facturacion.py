# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/soldados/soldados_facturacion.py

from apps.sarita_agents.agents.soldado_n6_oro_v2 import SoldadoN6OroV2
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class SoldadoGeneracionFactura(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "FacturaVenta"
    required_permissions = ["prestadores.execute"]
    event_name = "INVOICE_GENERATED"

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO FACTURACIÓN: Generando factura para operación {params.get('operacion_id')}")
        from apps.prestadores.mi_negocio.gestion_comercial.services import FacturacionService
        from apps.prestadores.mi_negocio.gestion_comercial.domain.models import OperacionComercial

        operacion_id = params.get('operacion_id')
        operacion = OperacionComercial.objects.get(id=operacion_id)

        factura = FacturacionService.facturar_operacion_confirmada(operacion)
        return factura

class SoldadoValidacionDIAN(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "FacturaVenta"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO FACTURACIÓN: Validando estado DIAN de factura {params.get('factura_id')}")
        from apps.prestadores.mi_negocio.gestion_comercial.domain.models import FacturaVenta
        factura = FacturaVenta.objects.get(id=params.get('factura_id'))
        # Simulación de consulta a servicio DIAN real
        return {
            "id": str(factura.id),
            "number": factura.number,
            "estado_dian": factura.estado_dian,
            "cufe": factura.cufe
        }

class SoldadoNotificacionFactura(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "FacturaVenta"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO FACTURACIÓN: Notificando factura al cliente.")
        # Lógica de envío de correo/SMS
        return {"status": "SENT", "msg": "Factura enviada al cliente."}

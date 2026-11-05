import logging
from django.dispatch import receiver
# from apps.prestadores.mi_negocio.gestion_comercial.signals import factura_comercial_confirmada

logger = logging.getLogger(__name__)

# @receiver(factura_comercial_confirmada)
def handle_factura_confirmada(sender, **kwargs):
    """
    Receptor de la señal que se activa cuando una factura comercial es confirmada.
    Este es el punto de entrada para el módulo de facturación.
    """
    factura = kwargs.get('factura')
    if not factura:
        return

    log_context = {
        "user_id": factura.creado_por.id,
        "profile_id": factura.perfil.id,
        "action": "PROCESS_COMMERCIAL_INVOICE",
        "invoice_id": factura.id,
        "source_module": "gestion_comercial",
        "destination_module": "facturacion",
    }

    logger.info(
        f"Señal 'factura_comercial_confirmada' recibida para la Factura ID: {factura.id}. "
        f"Iniciando procesamiento en el módulo de facturación.",
        extra=log_context
    )

    # --- Lógica futura del módulo de facturación iría aquí ---
    # 1. Validar reglas contables.
    # 2. Calcular impuestos finales.
    # 3. Crear el modelo de `FacturaContable`.
    # 4. Devolver el resultado o emitir un nuevo evento.

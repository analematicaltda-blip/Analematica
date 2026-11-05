import logging
from shared.subscribers import subscribe

logger = logging.getLogger(__name__)

def handle_lead_created_event(payload: dict):
    """
    Este es el handler que se ejecutará cuando se reciba un evento 'lead.created'.
    """
    logger.info(f"Received lead.created event! Processing payload: {payload}")
    # En el futuro, aquí irá la lógica para buscar y disparar workflows.

def register_subscribers():
    """
    Función para registrar todos los suscriptores de este módulo.
    Debe ser llamada al iniciar la aplicación.
    """
    subscribe('lead.created', handle_lead_created_event)

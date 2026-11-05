# Registro de suscriptores a eventos de dominio
# Mapea event_type -> lista de funciones handler

EVENT_SUBSCRIBERS = {}

def subscribe(event_type: str, handler_func):
    """
    Añade un handler a la lista de suscriptores para un tipo de evento.
    """
    if event_type not in EVENT_SUBSCRIBERS:
        EVENT_SUBSCRIBERS[event_type] = []
    EVENT_SUBSCRIBERS[event_type].append(handler_func)

def get_subscribers_for_event(event_type: str):
    """
    Obtiene todos los handlers suscritos a un tipo de evento.
    """
    return EVENT_SUBSCRIBERS.get(event_type, [])

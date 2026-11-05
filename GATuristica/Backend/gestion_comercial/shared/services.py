from .models import DomainEvent

class EventDispatcher:
    @staticmethod
    def dispatch(event_type: str, payload: dict):
        """
        Crea un nuevo DomainEvent en la base de datos para ser procesado asíncronamente.
        """
        DomainEvent.objects.create(event_type=event_type, payload=payload)

# Instancia global para ser usada por otros módulos
event_dispatcher = EventDispatcher()

# funnels/runtime/engine.py
from django.db import transaction
from .events import FunnelEventType, is_event_supported
from .executor import execute_form_submit, find_start_page_id
from funnels.models import FunnelPublication, FunnelVersion, Lead, LeadState, LeadEvent

@transaction.atomic
def process_event(publication_slug: str, event_type: str, payload: dict):
    """
    Punto de entrada principal del motor de ejecución.
    Procesa un evento para un embudo publicado.
    """
    if not is_event_supported(event_type):
        raise ValueError(f"Event type '{event_type}' is not supported.")

    try:
        publication = FunnelPublication.objects.select_related('funnel', 'version').get(public_url_slug=publication_slug, is_active=True)
    except FunnelPublication.DoesNotExist:
        raise ValueError(f"Active publication with slug '{publication_slug}' not found.")

    funnel = publication.funnel
    version = publication.version
    schema = version.schema_json

    # Para el MVP, nos centramos en el evento que crea un Lead.
    if event_type == FunnelEventType.FORM_SUBMIT:
        # El executor se encarga de la lógica específica del evento
        lead, lead_state = execute_form_submit(
            tenant=funnel.tenant,
            funnel=funnel,
            version=version,
            form_data=payload.get('form_data', {}),
            page_id=payload.get('page_id')
        )

        # Registrar el evento
        LeadEvent.objects.create(
            lead=lead,
            event_type=event_type,
            payload=payload,
            page_id=lead_state.current_page_id
        )

        return lead

    # Lógica para otros eventos (ej. PAGE_VIEW) se añadiría aquí.
    # Por ejemplo, encontrar un lead existente por un ID de sesión en el payload
    # y actualizar su estado.

    return None # O el lead actualizado si corresponde

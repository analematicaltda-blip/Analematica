# funnels/runtime/executor.py
from funnels.models import Tenant, Funnel, FunnelVersion, Lead, LeadState

def find_start_page_id(schema: dict) -> str | None:
    """
    Encuentra el ID de la primera página en el schema del embudo.
    Asume que las páginas están ordenadas.
    """
    pages = schema.get('pages', [])
    if pages:
        return pages[0].get('id')
    return None

def execute_form_submit(tenant: Tenant, funnel: Funnel, version: FunnelVersion, form_data: dict, page_id: str):
    """
    Ejecuta la lógica para un evento FORM_SUBMIT.
    Para el MVP, esto siempre crea un nuevo Lead y su estado inicial.
    """
    if not page_id:
        raise ValueError("page_id is required for FORM_SUBMIT.")

    # 1. Crear el Lead
    lead = Lead.objects.create(
        tenant=tenant,
        funnel=funnel,
        initial_version=version,
        form_data=form_data
    )

    # 2. Crear el estado inicial del Lead.
    # Para un FORM_SUBMIT, el estado actual es la página donde se envió el formulario.
    # En un flujo más complejo, podríamos buscar la siguiente página.
    lead_state = LeadState.objects.create(
        lead=lead,
        current_page_id=page_id,
        current_status='active', # O 'completed' si este es el final del embudo
        version=version
    )

    return lead, lead_state

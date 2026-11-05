# funnels/runtime_models.py
import uuid
from django.db import models
try:
    from infrastructure.models import Tenant, User
except (ImportError, ValueError):
    from ..infrastructure.models import Tenant, User
from .models import Funnel, FunnelVersion

class Lead(models.Model):
    """
    Representa un lead único capturado a través de un embudo.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='leads')
    funnel = models.ForeignKey(Funnel, on_delete=models.CASCADE, related_name='runtime_leads')
    initial_version = models.ForeignKey(FunnelVersion, on_delete=models.PROTECT, related_name='leads_started')

    # Almacena los datos del formulario que crearon el lead
    form_data = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lead {self.id} in {self.funnel.name}"

class LeadState(models.Model):
    """
    Rastrea el estado actual de un lead dentro de la ejecución de un embudo.
    Permite reanudar la ejecución.
    """
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name='state')
    current_page_id = models.CharField(max_length=255, help_text="ID de la página actual del funnel (del schema_json)")
    current_status = models.CharField(max_length=100, default='active') # ej. active, completed, failed

    # Puede almacenar datos adicionales recogidos durante el flujo
    execution_context = models.JSONField(default=dict)

    version = models.ForeignKey(FunnelVersion, on_delete=models.PROTECT, related_name='active_lead_states')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"State for Lead {self.lead_id} at page {self.current_page_id}"

class LeadEvent(models.Model):
    """
    Log de auditoría inmutable para cada evento que ocurre durante la ejecución del embudo de un lead.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=100) # ej. PAGE_VIEW, FORM_SUBMIT

    # Guarda el payload del evento
    payload = models.JSONField(default=dict)

    # Metadata sobre dónde ocurrió el evento
    page_id = models.CharField(max_length=255, null=True, blank=True)
    block_id = models.CharField(max_length=255, null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Event '{self.event_type}' for Lead {self.lead_id} at {self.timestamp}"

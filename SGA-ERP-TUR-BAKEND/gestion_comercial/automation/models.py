# automation/models.py
from django.db import models
from infrastructure.models import Tenant
from .models_sales import Lead

class AgentPersona(models.Model):
    """
    Define la personalidad, el rol y las capacidades de un agente de IA.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='agent_personas')
    name = models.CharField(max_length=255, unique=True)
    role_description = models.TextField(help_text="Descripción del rol, ej. 'Asistente de ventas experto en moda'")
    tone = models.CharField(max_length=100, help_text="Ej. 'Amigable y servicial', 'Profesional y directo'")

    # El prompt base que define el comportamiento del agente
    base_prompt = models.TextField(help_text="El prompt de sistema que guía a la IA.")

    # En el futuro, podríamos limitar qué herramientas puede usar cada persona
    # allowed_tools = models.JSONField(default=list, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Los modelos de Workflow, Node y Edge se mantienen para futuras fases.
class Workflow(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='workflows')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Node(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='nodes')
    node_type = models.CharField(max_length=100) # ej. 'trigger', 'action'
    config_json = models.JSONField(default=dict)

class Edge(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='edges')
    source_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='outgoing_edges')
    target_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='incoming_edges')

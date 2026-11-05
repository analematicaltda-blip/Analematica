import uuid
from django.db import models
try:
    from infrastructure.models import Tenant
except (ImportError, ValueError):
    from ..infrastructure.models import Tenant

class CadenaTurismo(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='cadenas')
    nombre = models.CharField(max_length=255)
    color_primario = models.CharField(max_length=7)
    color_secundario = models.CharField(max_length=7)
    def __str__(self): return self.nombre

class FunnelCategoria(models.Model):
    cadena = models.ForeignKey(CadenaTurismo, on_delete=models.CASCADE, related_name='categorias')
    nombre = models.CharField(max_length=255)
    icon = models.CharField(max_length=50, blank=True)
    def __str__(self): return self.nombre

class FunnelSubcategoria(models.Model):
    categoria = models.ForeignKey(FunnelCategoria, on_delete=models.CASCADE, related_name='subcategorias')
    nombre = models.CharField(max_length=255)
    def __str__(self): return self.nombre

class FunnelLandingPage(models.Model):
    subcategoria = models.ForeignKey(FunnelSubcategoria, on_delete=models.CASCADE, related_name='landing_pages')
    nombre = models.CharField(max_length=255)
    publicada = models.BooleanField(default=False)
    def __str__(self): return self.nombre

class Funnel(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')]
    landing_page = models.ForeignKey(FunnelLandingPage, on_delete=models.CASCADE, related_name='funnels', null=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='funnels')
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return self.name

class FunnelVersion(models.Model):
    funnel = models.ForeignKey(Funnel, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    schema_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    class Meta:
        unique_together = ('funnel', 'version_number')
        ordering = ['-version_number']
    def __str__(self): return f"{self.funnel.name} - v{self.version_number}"

class FunnelPage(models.Model):
    funnel_version = models.ForeignKey(FunnelVersion, on_delete=models.CASCADE, related_name='pages')
    page_type = models.CharField(max_length=100)
    page_schema_json = models.JSONField(default=dict)
    order_index = models.PositiveIntegerField()
    class Meta: ordering = ['order_index']
    def __str__(self): return f"Page {self.order_index} ({self.page_type}) for {self.funnel_version}"

class FunnelPublication(models.Model):
    funnel = models.ForeignKey(Funnel, on_delete=models.CASCADE, related_name='publications')
    version = models.ForeignKey(FunnelVersion, on_delete=models.CASCADE, related_name='publications')
    public_url_slug = models.SlugField(unique=True, default=uuid.uuid4)
    published_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return f"Publication of {self.funnel.name} v{self.version.version_number} at /{self.public_url_slug}"

class LeadCapture(models.Model):
    funnel = models.ForeignKey(Funnel, on_delete=models.CASCADE, related_name='leads')
    version = models.ForeignKey(FunnelVersion, on_delete=models.CASCADE, related_name='leads')
    page = models.ForeignKey(FunnelPage, on_delete=models.CASCADE, related_name='leads')
    form_data = models.JSONField(default=dict)
    captured_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Lead captured in {self.funnel.name} at {self.captured_at}"

class FunnelEvent(models.Model):
    EVENT_TYPES = [('page_view', 'Page View'), ('submit', 'Form Submit'), ('conversion', 'Conversion')]
    funnel = models.ForeignKey(Funnel, on_delete=models.CASCADE, related_name='events')
    version = models.ForeignKey(FunnelVersion, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    metadata_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Event '{self.event_type}' on {self.funnel.name}"

# Importar los modelos de runtime al final para evitar importaciones circulares.
from .runtime_models import Lead, LeadState, LeadEvent

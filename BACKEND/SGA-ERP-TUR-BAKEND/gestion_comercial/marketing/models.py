# marketing/models.py
from django.db import models
try:
    from infrastructure.models import Tenant
except (ImportError, ValueError):
    from ..infrastructure.models import Tenant
# from funnels.runtime_models import Lead # Se elimina para evitar importación circular

class Campaign(models.Model):
    """
    Representa una campaña de marketing unificada.
    """
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('scheduled', 'Programada'),
        ('sending', 'Enviando'),
        ('sent', 'Enviada'),
        ('archived', 'Archivada'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='campaigns')
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Podríamos vincular una campaña a un segmento de leads específico
    target_leads = models.ManyToManyField('gestion_comercial.Lead', blank=True, related_name='marketing_campaigns')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CampaignChannel(models.Model):
    """
    Define un canal específico para una campaña (ej. Email, SMS).
    """
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='channels')
    channel_type = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    is_active = models.BooleanField(default=False)

    # Podría contener métricas específicas del canal
    sent_count = models.PositiveIntegerField(default=0)
    open_rate = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.campaign.name} - {self.get_channel_type_display()}"

class MarketingContent(models.Model):
    """
    Almacena el contenido maestro para una campaña, que puede ser
    adaptado para diferentes canales.
    """
    campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE, related_name='content')
    subject = models.CharField(max_length=255, blank=True, help_text="Asunto para emails")
    body_text = models.TextField(blank=True, help_text="Contenido principal en texto plano o Markdown")
    body_html = models.TextField(blank=True, help_text="Contenido HTML para emails")

    # Podríamos añadir campos para imágenes, videos, etc.
    # main_image_url = models.URLField(blank=True)

    def __str__(self):
        return f"Content for {self.campaign.name}"

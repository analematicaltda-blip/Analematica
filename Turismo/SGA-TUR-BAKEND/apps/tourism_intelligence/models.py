from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.turismo.models.provider_models import BaseModel

class ConversationalIntent(BaseModel):
    """
    Vía 3: Inteligencia Conversacional.
    Clasifica las intenciones de los turistas en los chats.
    """
    class IntentType(models.TextChoices):
        SEARCH_HOTEL = 'SEARCH_HOTEL', _('Búsqueda de Alojamiento')
        SEARCH_FOOD = 'SEARCH_FOOD', _('Búsqueda de Restaurante')
        BOOKING_REQUEST = 'BOOKING_REQUEST', _('Solicitud de Reserva')
        PRICING_QUERY = 'PRICING_QUERY', _('Consulta de Precios')
        HOW_TO_ARRIVE = 'HOW_TO_ARRIVE', _('Consulta de Ubicación/GPS')
        SERVICE_COMPLAINT = 'SERVICE_COMPLAINT', _('Queja o Reclamo')
        POSITIVE_FEEDBACK = 'POSITIVE_FEEDBACK', _('Comentario Positivo')

    conversation_id = models.UUIDField(db_index=True)
    message_id = models.UUIDField(db_index=True)
    tourist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    intent = models.CharField(max_length=50, choices=IntentType.choices)
    confidence_score = models.FloatField(default=0.0)
    sentiment_score = models.FloatField(default=0.0) # -1.0 a 1.0
    detected_entities = models.JSONField(default=dict) # Ej: {"destino": "Puerto Gaitán"}

    def __str__(self):
        return f"{self.intent} ({self.confidence_score})"

class ConversationalKPI(BaseModel):
    """
    Indicadores de calidad de respuesta por prestador.
    """
    provider = models.ForeignKey('turismo.TourismProvider', on_delete=models.CASCADE, related_name='chat_kpis')
    avg_response_time_seconds = models.FloatField(default=0.0)
    response_rate = models.FloatField(default=0.0) # 0.0 a 1.0
    total_chats = models.PositiveIntegerField(default=0)
    missed_chats = models.PositiveIntegerField(default=0)
    period = models.CharField(max_length=20) # YYYY-MM

    class Meta:
        unique_together = ('provider', 'period')

class TourismDemandForecast(BaseModel):
    """
    Motor de predicción de demanda por destino y categoría.
    """
    destino = models.CharField(max_length=255)
    categoria_servicio = models.CharField(max_length=100) # HOTEL, RESTAURANT, etc.
    fecha = models.DateField()
    demanda_estimada = models.PositiveIntegerField()
    demanda_real = models.PositiveIntegerField(null=True, blank=True)
    precision_modelo = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('destino', 'categoria_servicio', 'fecha')

class TourismSeasonality(BaseModel):
    """
    Planificación de temporadas territoriales.
    """
    class DemandLevel(models.TextChoices):
        LOW = 'LOW', _('Temporada Baja')
        MEDIUM = 'MEDIUM', _('Temporada Media')
        HIGH = 'HIGH', _('Temporada Alta')

    destino = models.CharField(max_length=255)
    mes = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 13)])
    nivel_demanda = models.CharField(max_length=10, choices=DemandLevel.choices)
    categoria_destacada = models.CharField(max_length=100, blank=True)

class TouristBehaviorProfile(BaseModel):
    """
    Segmentación inteligente del turista.
    """
    class TouristSegment(models.TextChoices):
        ADVENTURER = 'ADVENTURER', _('Turista Aventurero')
        GASTRONOMIC = 'GASTRONOMIC', _('Turista Gastronómico')
        CULTURAL = 'CULTURAL', _('Turista Cultural')
        ECOLOGICAL = 'ECOLOGICAL', _('Turista Ecológico')
        FAMILY = 'FAMILY', _('Turista Familiar')

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='behavior_profile')
    destinos_visitados = models.JSONField(default=list)
    categorias_preferidas = models.JSONField(default=list)
    ticket_promedio = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    frecuencia_viajes_anual = models.PositiveIntegerField(default=0)
    segmento_asignado = models.CharField(max_length=20, choices=TouristSegment.choices, null=True, blank=True)

class TourismFlowAnalytics(BaseModel):
    """
    Análisis de flujos de movilidad turística.
    """
    origen_visitante = models.CharField(max_length=255)
    destino = models.CharField(max_length=255)
    fecha = models.DateField()
    volumen_visitantes = models.PositiveIntegerField(default=0)

class TourismEconomicImpact(BaseModel):
    """
    KPIs económicos para el sistema SADI.
    """
    destino = models.CharField(max_length=255)
    periodo = models.CharField(max_length=50) # Ej: "2026-Q1"
    ventas_totales = models.DecimalField(max_digits=18, decimal_places=2)
    ingresos_turisticos_netos = models.DecimalField(max_digits=18, decimal_places=2)
    empleo_generado_estimado = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('destino', 'periodo')

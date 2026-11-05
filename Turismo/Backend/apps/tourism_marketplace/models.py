from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.turismo.models.provider_models import TourismProvider, TourismService, BaseModel

class ProviderReputation(BaseModel):
    """
    Gestiona el prestigio y confiabilidad de los prestadores en el marketplace.
    """
    provider = models.OneToOneField(TourismProvider, on_delete=models.CASCADE, related_name='reputation')
    rating_promedio = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    reservas_completadas = models.PositiveIntegerField(default=0)
    cancelaciones = models.PositiveIntegerField(default=0)
    indice_confiabilidad = models.FloatField(default=1.0, help_text="Escala 0.0 a 1.0")

    def __str__(self):
        return f"Reputación: {self.provider.name} ({self.rating_promedio})"

class TourismReview(BaseModel):
    """
    Reseñas directas de clientes a productos/servicios del marketplace.
    """
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='marketplace_reviews')
    service = models.ForeignKey(TourismService, on_delete=models.CASCADE, related_name='marketplace_reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)

    class Meta:
        unique_together = ('customer', 'service')

class ProductRanking(BaseModel):
    """
    Almacena los índices calculados para el algoritmo de descubrimiento.
    """
    service = models.OneToOneField(TourismService, on_delete=models.CASCADE, related_name='ranking')
    indice_popularidad = models.FloatField(default=0.0)
    indice_conversion = models.FloatField(default=0.0)
    indice_reputacion = models.FloatField(default=0.0)
    score_total = models.FloatField(default=0.0, db_index=True)

    def calculate_total_score(self):
        # Fórmula: (0.4 reputación) + (0.3 reservas) + (0.2 conversión) + (0.1 actividad reciente)
        # Nota: Los índices deben estar normalizados
        self.score_total = (0.4 * self.indice_reputacion) + \
                           (0.3 * self.indice_popularidad) + \
                           (0.2 * self.indice_conversion) + 0.1
        self.save()

class TourismPromotion(BaseModel):
    """
    Sistema de promoción institucional o pagada.
    """
    class PromotionType(models.TextChoices):
        PROMOTED = 'PROMOTED', _('Promocionado')
        SPECIAL_OFFER = 'SPECIAL_OFFER', _('Oferta Especial')
        FEATURED = 'FEATURED', _('Destacado')

    service = models.ForeignKey(TourismService, on_delete=models.CASCADE, related_name='promotions')
    tipo_promocion = models.CharField(max_length=20, choices=PromotionType.choices)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    prioridad = models.PositiveIntegerField(default=1)

class TourismConversionMetrics(BaseModel):
    """
    Métricas de rendimiento del marketplace por producto.
    """
    service = models.OneToOneField(TourismService, on_delete=models.CASCADE, related_name='conversion_metrics')
    visitas = models.PositiveIntegerField(default=0)
    reservas = models.PositiveIntegerField(default=0)
    conversion_rate = models.FloatField(default=0.0)
    ingresos_generados = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    def update_rate(self):
        if self.visitas > 0:
            self.conversion_rate = (self.reservas / self.visitas) * 100
            self.save()

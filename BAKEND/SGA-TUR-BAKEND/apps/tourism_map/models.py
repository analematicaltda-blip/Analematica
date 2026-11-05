from django.db import models
import uuid

class TourismLocation(models.Model):
    """
    Hallazgo 22: Sistema de Mapa Turístico Inteligente.
    Almacena destinos, hoteles, tours y puntos de interés georreferenciados.
    """
    LOCATION_TYPES = [
        ('hotel', 'Hotel'),
        ('tour', 'Tour / Excursión'),
        ('restaurante', 'Restaurante'),
        ('atraccion', 'Atracción Turística'),
        ('guia', 'Servicio de Guía'),
        ('transporte', 'Punto de Transporte'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=LOCATION_TYPES)
    description = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='República Dominicana')
    rating = models.FloatField(default=0.0)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

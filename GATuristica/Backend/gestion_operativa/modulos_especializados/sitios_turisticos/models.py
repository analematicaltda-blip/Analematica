# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/sitios_turisticos/models.py
from django.db import models
from django.conf import settings
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile

class SitioTuristico(models.Model):
    """
    Representa un sitio turístico gestionado por un prestador.
    Esto puede ser un parque, un mirador, una finca, etc.
    """
    TIPO_SITIO_CHOICES = [
        ('parque_tematico', 'Parque Temático'),
        ('reserva_natural', 'Reserva Natural'),
        ('museo', 'Museo'),
        ('centro_cultural', 'Centro Cultural'),
        ('mirador', 'Mirador'),
        ('finca_agroturistica', 'Finca Agroturística'),
        ('otro', 'Otro'),
    ]

    perfil = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='sitios_turisticos')
    nombre = models.CharField(max_length=150)
    descripcion_corta = models.CharField(max_length=255)
    descripcion_larga = models.TextField()
    tipo_sitio = models.CharField(max_length=30, choices=TIPO_SITIO_CHOICES, default='otro')

    ubicacion_latitud = models.FloatField(null=True, blank=True)
    ubicacion_longitud = models.FloatField(null=True, blank=True)
    direccion_texto = models.CharField(max_length=255, blank=True, help_text="Dirección o indicaciones de cómo llegar.")

    horario_apertura = models.TimeField(null=True, blank=True)
    horario_cierre = models.TimeField(null=True, blank=True)
    dias_operacion = models.CharField(max_length=100, blank=True, help_text="Ej: Lunes a Viernes, Fines de semana")

    precio_entrada_adulto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    precio_entrada_nino = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    activo = models.BooleanField(default=True, help_text="Indica si el sitio está abierto al público.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

class ActividadEnSitio(models.Model):
    """
    Representa una actividad específica que se puede realizar dentro de un sitio turístico.
    Ej: Canopy en una reserva, taller de café en una finca.
    """
    sitio = models.ForeignKey(SitioTuristico, on_delete=models.CASCADE, related_name='actividades')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    duracion_estimada_minutos = models.PositiveIntegerField(null=True, blank=True)
    precio_adicional = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Costo adicional a la entrada del sitio.")
    requiere_reserva = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} en {self.sitio.nombre}"

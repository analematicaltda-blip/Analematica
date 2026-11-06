# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/agencias_de_viajes/models.py
from django.db import models
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from django.conf import settings

class PaqueteTuristico(models.Model):
    """
    Representa un paquete turístico ofrecido por una agencia de viajes.
    """
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('publicado', 'Publicado'),
        ('archivado', 'Archivado'),
    ]

    perfil = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='paquetes_turisticos')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    duracion_dias = models.PositiveIntegerField(default=1)
    precio_por_persona = models.DecimalField(max_digits=10, decimal_places=2)
    # Lista de IDs de productos/servicios incluidos, gestionados en el frontend.
    servicios_incluidos = models.JSONField(default=list, blank=True, help_text="Lista de IDs de productos/servicios genéricos incluidos.")
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='borrador')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.duracion_dias} días)"

class ReservaPaquete(models.Model):
    """
    Representa una reserva de un paquete turístico por parte de un cliente.
    """
    ESTADO_RESERVA_CHOICES = [
        ('pendiente', 'Pendiente de Confirmación'),
        ('confirmada', 'Confirmada'),
        ('pagada', 'Pagada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]

    paquete = models.ForeignKey(PaqueteTuristico, on_delete=models.CASCADE, related_name='reservas')
    # Podría enlazarse con el modelo Cliente si existe y es relevante.
    # cliente = models.ForeignKey('gestion_comercial.Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    nombre_cliente_temporal = models.CharField(max_length=150, help_text="Nombre del cliente que hace la reserva")
    email_cliente = models.EmailField()
    telefono_cliente = models.CharField(max_length=20, blank=True)

    fecha_inicio = models.DateField()
    numero_de_personas = models.PositiveIntegerField(default=1)
    costo_total = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=15, choices=ESTADO_RESERVA_CHOICES, default='pendiente')
    notas_especiales = models.TextField(blank=True, help_text="Requerimientos o notas especiales del cliente.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calcula el costo total al guardar la reserva si no se ha especificado
        if not self.costo_total:
            self.costo_total = self.paquete.precio_por_persona * self.numero_de_personas
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reserva de {self.paquete.nombre} para {self.nombre_cliente_temporal} el {self.fecha_inicio}"

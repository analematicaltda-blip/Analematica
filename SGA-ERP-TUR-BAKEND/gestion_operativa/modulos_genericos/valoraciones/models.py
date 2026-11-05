from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from ..productos_servicios.models import Product
from api.models import CustomUser # El usuario turista

class Valoracion(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='valoraciones')
    # El perfil del prestador que recibe la valoración
    perfil_prestador = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='valoraciones_recibidas')
    # El turista que escribe la valoración
    turista = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='valoraciones_emitidas')

    puntuacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    # El prestador puede marcar una respuesta a la valoración
    respuesta_del_prestador = models.TextField(blank=True, null=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('producto', 'turista') # Un turista solo puede valorar un producto una vez
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Valoración de {self.turista} para {self.producto.nombre} ({self.puntuacion} estrellas)"

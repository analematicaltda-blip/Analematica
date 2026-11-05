from django.db import models
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import TenantAwareModel

class EvidenciaGaleria(TenantAwareModel):
    """
    Repositorio de imágenes de evidencia operativa.
    """
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    imagen_url = models.URLField()
    fecha_captura = models.DateTimeField(auto_now_add=True)

    orden_id = models.UUIDField(null=True, blank=True)
    tarea_id = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return self.titulo

    class Meta(TenantAwareModel.Meta):
        app_label = 'mi_negocio'

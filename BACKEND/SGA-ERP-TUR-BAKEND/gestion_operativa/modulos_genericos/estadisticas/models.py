from django.db import models
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import TenantAwareModel

class RegistroDeEstadisticas(TenantAwareModel):
    """
    Agregaciones de métricas operativas por periodo.
    """
    periodo_inicio = models.DateField()
    periodo_fin = models.DateField()

    ordenes_completadas = models.IntegerField(default=0)
    incidentes_reportados = models.IntegerField(default=0)
    costo_operativo_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    productividad_promedio = models.FloatField(default=0.0)

    def __str__(self):
        return f"Métricas {self.periodo_inicio} a {self.periodo_fin}"

    class Meta(TenantAwareModel.Meta):
        app_label = 'mi_negocio'

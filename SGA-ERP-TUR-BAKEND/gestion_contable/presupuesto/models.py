# from django.db import models
# from django.conf import settings
# from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
# from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import ChartOfAccount
#
# class Presupuesto(models.Model):
#     perfil = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='presupuestos')
#     nombre = models.CharField(max_length=255)
#     ano_fiscal = models.PositiveIntegerField()
#     total_ingresos_presupuestado = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
#     total_gastos_presupuestado = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
#
#     class Meta:
#         unique_together = ('perfil', 'ano_fiscal')
#
#     def __str__(self):
#         return f"{self.nombre} ({self.ano_fiscal})"
#
# class PartidaPresupuestal(models.Model):
#     class Tipo(models.TextChoices):
#         INGRESO = 'INGRESO', 'Ingreso'
#         GASTO = 'GASTO', 'Gasto'
#
#     presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name='partidas')
#     cuenta_contable = models.ForeignKey(ChartOfAccount, on_delete=models.PROTECT, related_name='partidas_presupuestales')
#     tipo = models.CharField(max_length=10, choices=Tipo.choices)
#     monto_presupuestado = models.DecimalField(max_digits=18, decimal_places=2)
#     monto_ejecutado = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
#
#     def __str__(self):
#         return f"Partida para {self.cuenta_contable.name} - {self.monto_presupuestado}"
#
# class EjecucionPresupuestal(models.Model):
#     partida = models.ForeignKey(PartidaPresupuestal, on_delete=models.CASCADE, related_name='ejecuciones')
#     fecha = models.DateField()
#     monto = models.DecimalField(max_digits=18, decimal_places=2)
#     descripcion = models.CharField(max_length=255)
#     # Generic foreign key to link to the source document (e.g., FacturaCompra, Planilla)
#     from django.contrib.contenttypes.fields import GenericForeignKey
#     from django.contrib.contenttypes.models import ContentType
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     origin_document = GenericForeignKey('content_type', 'object_id')
#
#     def __str__(self):
#         return f"Ejecución de {self.monto} en {self.fecha} para {self.partida}"

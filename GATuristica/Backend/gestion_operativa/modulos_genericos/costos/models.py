from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile

class Costo(models.Model):
    """
    Modelo para gestionar los costos operativos de un prestador.
    """
    perfil = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='costos')
    concepto = models.CharField(_("Concepto del Costo"), max_length=255)
    monto = models.DecimalField(_("Monto"), max_digits=12, decimal_places=2)
    fecha = models.DateField(_("Fecha del Costo"))
    es_recurrente = models.BooleanField(_("¿Es Recurrente?"), default=False)

    class Tipo(models.TextChoices):
        FIJO = 'FIJO', _('Fijo')
        VARIABLE = 'VARIABLE', _('Variable')
        INSUMOS = 'INSUMOS', _('Insumos / Materia Prima')
        PERSONAL = 'PERSONAL', _('Mano de Obra')
        TALLER = 'TALLER', _('Gastos de Taller/Cocina')

    tipo_costo = models.CharField(_("Tipo de Costo"), max_length=50, choices=Tipo.choices, default=Tipo.VARIABLE)

    # Vínculo con operación genérica
    orden_operativa_ref_id = models.UUIDField(null=True, blank=True, help_text="Vínculo con la orden que generó el gasto.")
    insumo_ref_id = models.UUIDField(null=True, blank=True, help_text="Vínculo con el ítem de inventario si aplica.")
    personal_ref_id = models.UUIDField(null=True, blank=True, help_text="Vínculo con el colaborador si es mano de obra.")

    def __str__(self):
        return f"{self.concepto} - ${self.monto}"

    class Meta:
        verbose_name = "Costo Operativo"
        verbose_name_plural = "Costos Operativos"
        ordering = ['-fecha']

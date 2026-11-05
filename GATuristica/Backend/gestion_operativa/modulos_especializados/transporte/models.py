from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import TenantAwareModel
from apps.core.catalogs.models import Vehicle as CatalogVehicle
# Asumimos TeamMember y Reservation de módulos genéricos futuros
# from ..personal.models import TeamMember
# from ..reservas.models import Reservation

class Vehicle(TenantAwareModel):
    """
    Representa un vehículo en la flota de la transportadora.
    """
    class VehicleStatus(models.TextChoices):
        AVAILABLE = 'AVAILABLE', _('Disponible')
        IN_SERVICE = 'IN_SERVICE', _('En Servicio')
        MAINTENANCE = 'MAINTENANCE', _('En Mantenimiento')
        INACTIVE = 'INACTIVE', _('Inactivo')

    catalog_reference = models.ForeignKey(CatalogVehicle, on_delete=models.SET_NULL, null=True, blank=True)
    nombre = models.CharField(_("Nombre Identificativo"), max_length=150)
    placa = models.CharField(_("Placa"), max_length=10, unique=True)
    modelo_ano = models.PositiveIntegerField(_("Modelo (Año)"))
    tipo_vehiculo = models.CharField(_("Tipo"), max_length=50) # Ej: Van, Bus
    capacidad = models.PositiveSmallIntegerField(_("Capacidad de Pasajeros"), default=1)
    status = models.CharField(_("Estado"), max_length=20, choices=VehicleStatus.choices, default=VehicleStatus.AVAILABLE)

    # Campos de cumplimiento
    insurance_expiry_date = models.DateField(_("Vencimiento de Póliza"))
    tech_inspection_expiry_date = models.DateField(_("Vencimiento Revisión T-M"))

    def __str__(self):
        return f"{self.nombre} ({self.placa})"

    class Meta:
        app_label = 'prestadores'

# class MaintenanceOrder(TenantAwareModel):
#     """
#     Una orden de trabajo para mantenimiento de un vehículo.
#     """
#     class MaintenanceType(models.TextChoices):
#         PREVENTIVE = 'PREVENTIVE', _('Preventivo')
#         CORRECTIVE = 'CORRECTIVE', _('Correctivo')
#
#     vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_orders')
#     maintenance_type = models.CharField(max_length=20, choices=MaintenanceType.choices)
#     description = models.TextField()
#     reported_by = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, blank=True)
#     # ... otros campos como `fecha_completado`, `costo`, etc.

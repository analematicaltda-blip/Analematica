from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import TenantAwareModel
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product
from apps.core.catalogs.models import Amenity

class RoomType(TenantAwareModel):
    """
    Define un 'tipo' de habitación, que es en sí mismo un producto vendible.
    """
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='room_type_details'
    )
    capacidad = models.PositiveSmallIntegerField(_("Capacidad de Personas"))
    amenities = models.ManyToManyField(Amenity, blank=True)

    def __str__(self):
        return f"Detalles de Hotel para: {self.product.nombre}"

    class Meta:
        app_label = 'prestadores'

class Room(TenantAwareModel):
    """
    Representa una habitación física individual en el inventario.
    """
    class HousekeepingStatus(models.TextChoices):
        CLEAN = 'CLEAN', _('Limpia')
        DIRTY = 'DIRTY', _('Sucia')
        IN_PROGRESS = 'IN_PROGRESS', _('En Limpieza')
        INSPECTION = 'INSPECTION', _('Para Inspección')
        OUT_OF_ORDER = 'OUT_OF_ORDER', _('Fuera de Servicio')

    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')
    numero_habitacion = models.CharField(_("Número de Habitación"), max_length=10)
    housekeeping_status = models.CharField(
        _("Estado de Limpieza"),
        max_length=20,
        choices=HousekeepingStatus.choices,
        default=HousekeepingStatus.CLEAN
    )
    # Se podría añadir `area` o `piso`

    def __str__(self):
        return f"Habitación {self.numero_habitacion} ({self.room_type.product.nombre})"

    class Meta:
        unique_together = ('provider', 'numero_habitacion')
        app_label = 'prestadores'

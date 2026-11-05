import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField

# Corregido: La importación ahora apunta a los modelos locales del dominio operativo.
from ..perfil.models import TenantAwareModel, CategoriaPrestador as OperationalTag
from ..reservas.models import PoliticaCancelacion

class Product(TenantAwareModel):
    id_publico = models.UUIDField(editable=False, unique=True, null=True)
    """
    Modelo genérico para cualquier 'cosa' vendible o reservable.
    """
    class Tipo(models.TextChoices):
        PRODUCTO = 'PRODUCTO', _('Producto')
        SERVICIO = 'SERVICIO', _('Servicio')

    nombre = models.CharField(_("Nombre"), max_length=200)
    descripcion = models.TextField(_("Descripción"), blank=True)
    tipo = models.CharField(
        _("Tipo"),
        max_length=10,
        choices=Tipo.choices,
        default=Tipo.PRODUCTO
    )
    es_inventariable = models.BooleanField(
        _("Es Inventariable"),
        default=False,
        help_text=_("Marcar si este producto gestiona stock.")
    )
    stock = models.PositiveIntegerField(_("Stock Actual"), default=0, help_text=_("La cantidad actual de este producto en inventario."))
    base_price = MoneyField(_("Precio Base"), max_digits=19, decimal_places=2, default_currency='COP')

    is_packageable = models.BooleanField(_("Es Empaquetable"), default=False, help_text=_("¿Puede este servicio/producto ser parte de un paquete?"))
    operational_tags = models.ManyToManyField(OperationalTag, blank=True)
    cancellation_policy = models.ForeignKey(PoliticaCancelacion, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Producto/Servicio"
        verbose_name_plural = "Productos/Servicios"
        app_label = 'prestadores'

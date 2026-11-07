from django.db import models
from django.conf import settings
from apps.core_erp.base_models import BaseErpModel, TenantAwareModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.turismo.models import TourismProvider

class ProviderProfile(TourismProvider):
    """
    Proxy del modelo TourismProvider para retrocompatibilidad con el dominio business.
    Asegura que el ecosistema productivo herede del dominio central de Turismo.
    """
    class Meta:
        proxy = True
        verbose_name = "Provider Profile (Legacy Proxy)"
        app_label = 'domain_business'

    @property
    def commercial_name(self):
        return self.name

    @commercial_name.setter
    def commercial_name(self, value):
        self.name = value

class Reservation(TenantAwareModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        COMPLETED = 'COMPLETED', 'Completed'

    customer_id = models.UUIDField()

    # Generic Link to the item being reserved
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    item = GenericForeignKey('content_type', 'object_id')

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_price = models.DecimalField(max_digits=18, decimal_places=2)
    deposit_paid = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Reservation"
        app_label = 'domain_business'

class AdditionalService(TenantAwareModel):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='additional_services')
    service_id = models.UUIDField()
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        app_label = 'domain_business'

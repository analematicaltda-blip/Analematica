
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.orders.models import Order

class Payment(models.Model):
    """
    Representa una transacción de pago.
    """
    STATUS_CHOICES = [
        ('INIT', 'Iniciado'),
        ('PENDING', 'Pendiente'),
        ('PAID', 'Pagado'),
        ('FAILED', 'Fallido'),
        ('CANCELLED', 'Cancelado'),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='INIT')
    provider = models.CharField(
        _("Proveedor de Pago"),
        max_length=50,
        blank=True,
        help_text="Ej: 'Wompi', 'Stripe'"
    )
    transaction_id = models.CharField(
        _("ID de Transacción del Proveedor"),
        max_length=255,
        unique=True,
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pago {self.id} - {self.status} - ${self.amount}"

    class Meta:
        verbose_name = _("Pago")
        verbose_name_plural = _("Pagos")
        ordering = ['-created_at']

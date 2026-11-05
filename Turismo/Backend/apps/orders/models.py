
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.comercial.models import Plan

class Order(models.Model):
    """
    Representa una orden de compra, una instantánea de un carro en el momento del pago.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Orden #{self.id} de {self.user.username}"

    class Meta:
        verbose_name = _("Orden")
        verbose_name_plural = _("Órdenes")
        ordering = ['-created_at']

class OrderItem(models.Model):
    """
    Representa un ítem dentro de una orden.
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, related_name='order_items', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.plan.nombre} en {self.order}"

    class Meta:
        verbose_name = _("Ítem de Orden")
        verbose_name_plural = _("Ítems de Orden")


from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.comercial.models import Plan

class Cart(models.Model):
    """
    Representa el carro de compras de un usuario.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        null=True, blank=True, # Permite carros para invitados en el futuro
        help_text=_("El usuario dueño de este carro.")
    )
    session_key = models.CharField(
        max_length=40,
        null=True, blank=True,
        help_text=_("Clave de sesión para usuarios invitados.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Carro de {self.user.username}"
        return f"Carro de invitado (sesión {self.session_key})"

    class Meta:
        verbose_name = _("Carro de Compras")
        verbose_name_plural = _("Carros de Compras")


class CartItem(models.Model):
    """
    Representa un ítem dentro de un carro de compras.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.plan.nombre} en {self.cart}"

    @property
    def total_price(self):
        return self.plan.precio * self.quantity

    class Meta:
        verbose_name = _("Ítem del Carro")
        verbose_name_plural = _("Ítems del Carro")
        unique_together = ('cart', 'plan') # No permitir el mismo plan dos veces en el mismo carro

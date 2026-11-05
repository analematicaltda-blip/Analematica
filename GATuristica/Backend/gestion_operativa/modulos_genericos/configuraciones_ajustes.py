from django.db import models
from django.utils.translation import gettext_lazy as _
from .perfil.models import Perfil

class ConfiguracionPrestador(models.Model):
    """
    Modelo para guardar configuraciones y ajustes personales del prestador.
    """
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE, related_name='configuracion')

    # Ejemplo de configuración: Notificaciones
    recibir_notificaciones_email = models.BooleanField(
        _("Recibir notificaciones por correo electrónico"),
        default=True
    )
    recibir_notificaciones_push = models.BooleanField(
        _("Recibir notificaciones push en la aplicación"),
        default=True
    )

    # Ejemplo de configuración: Tema
    class TemaInterfaz(models.TextChoices):
        CLARO = 'CLARO', _('Claro')
        OSCURO = 'OSCURO', _('Oscuro')
        SISTEMA = 'SISTEMA', _('Automático (Sistema)')

    tema_interfaz = models.CharField(
        _("Tema de la Interfaz"),
        max_length=50,
        choices=TemaInterfaz.choices,
        default=TemaInterfaz.SISTEMA
    )

    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Configuración para {self.perfil.nombre_comercial}"

    class Meta:
        verbose_name = "Configuración de Prestador"
        verbose_name_plural = "Configuraciones de Prestadores"

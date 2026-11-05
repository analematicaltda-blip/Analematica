from django.db import models
from django.conf import settings

class DeviceToken(models.Model):
    """
    Hallazgo 10: Sistema de Notificaciones Push.
    Almacena los tokens de dispositivos registrados (FCM/APNs).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='device_tokens')
    token = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=20, choices=[('android', 'Android'), ('ios', 'iOS'), ('web', 'Web'), ('desktop', 'Desktop')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.platform}"

class ServiceLocation(models.Model):
    """
    Hallazgo 11: Geofencing para prestadores.
    Almacena las geocercas activas para prestadores de servicios.
    """
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='geofences')
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius = models.IntegerField(help_text="Radio de detección en metros")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Geocerca: {self.provider.email} ({self.latitude}, {self.longitude})"

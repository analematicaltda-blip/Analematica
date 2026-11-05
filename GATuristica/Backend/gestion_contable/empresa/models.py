from django.db import models
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile, TenantAwareModel

class InformacionEmpresa(TenantAwareModel):
    razon_social = models.CharField(max_length=255)
    nit = models.CharField(max_length=20, unique=True)
    direccion_legal = models.TextField(blank=True)
    telefono_contacto = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.razon_social

    class Meta(TenantAwareModel.Meta):
        app_label = 'empresa'

class Sucursal(TenantAwareModel):
    nombre = models.CharField(max_length=255)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20, blank=True)
    es_principal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} ({self.provider})"

    class Meta(TenantAwareModel.Meta):
        app_label = 'empresa'
        verbose_name_plural = "Sucursales"

class Tercero(TenantAwareModel):
    nombre = models.CharField(max_length=255)
    nit_o_cedula = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nombre

    class Meta(TenantAwareModel.Meta):
        app_label = 'empresa'
        unique_together = ('provider', 'nit_o_cedula')

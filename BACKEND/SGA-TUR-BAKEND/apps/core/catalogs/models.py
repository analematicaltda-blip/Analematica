from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Skill(BaseModel):
    class SkillType(models.TextChoices):
        SPECIALIZATION = 'SPECIALIZATION', _('Especialización')
        CERTIFICATION = 'CERTIFICATION', _('Certificación')
        LANGUAGE = 'LANGUAGE', _('Idioma')

    nombre = models.CharField(_("Nombre de la Competencia"), max_length=150)
    skill_type = models.CharField(_("Tipo"), max_length=20, choices=SkillType.choices)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = _("Habilidad / Competencia")
        verbose_name_plural = _("Habilidades y Competencias")

class Amenity(BaseModel):
    name = models.CharField(_("Nombre"), max_length=100)
    icon = models.CharField(_("Icono"), max_length=50, blank=True)
    category = models.CharField(_("Categoría"), max_length=50, default='GENERAL')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Comodidad / Amenidad")
        verbose_name_plural = _("Comodidades y Amenidades")

class Vehicle(BaseModel):
    class VehicleType(models.TextChoices):
        CAR = 'CAR', _('Automóvil')
        VAN = 'VAN', _('Van / Microbús')
        BUS = 'BUS', _('Autobús')
        BOAT = 'BOAT', _('Lancha / Bote')
        BIKE = 'BIKE', _('Bicicleta')
        MOTORCYCLE = 'MOTORCYCLE', _('Motocicleta')

    model_name = models.CharField(_("Modelo"), max_length=100)
    vehicle_type = models.CharField(_("Tipo"), max_length=20, choices=VehicleType.choices)
    capacity_max = models.PositiveIntegerField(_("Capacidad Máxima"), default=1)

    def __str__(self):
        return f"{self.model_name} ({self.get_vehicle_type_display()})"

    class Meta:
        verbose_name = _("Vehículo del Catálogo")
        verbose_name_plural = _("Vehículos del Catálogo")

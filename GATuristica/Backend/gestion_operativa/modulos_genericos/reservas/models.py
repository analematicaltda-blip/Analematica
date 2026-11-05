from apps.domain_business.operativa.models import (
    Reservation as Reserva,
    AdditionalService as ReservaServicioAdicional
)
from django.db import models

class PoliticaCancelacion(models.Model):
    perfil_ref_id = models.UUIDField()
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

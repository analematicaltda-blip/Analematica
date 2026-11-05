from django.db import models
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
import datetime

class Horario(models.Model):
    DIAS_SEMANA = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'),
        (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')
    ]
    perfil = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_apertura = models.TimeField()
    hora_cierre = models.TimeField()

    class Meta:
        unique_together = ('perfil', 'dia_semana')
        ordering = ['dia_semana', 'hora_apertura']

    def __str__(self):
        return f"{self.get_dia_semana_display()}: {self.hora_apertura.strftime('%H:%M')} - {self.hora_cierre.strftime('%H:%M')}"


class ExcepcionHorario(models.Model):
    perfil = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='excepciones_horario')
    fecha = models.DateField()
    esta_abierto = models.BooleanField(default=False)
    hora_apertura = models.TimeField(null=True, blank=True)
    hora_cierre = models.TimeField(null=True, blank=True)
    descripcion = models.CharField(max_length=255, help_text="Ej: Feriado Nacional, Evento Privado")

    class Meta:
        unique_together = ('perfil', 'fecha')
        ordering = ['fecha']

    def __str__(self):
        if self.esta_abierto:
            return f"Excepción el {self.fecha}: Abierto de {self.hora_apertura.strftime('%H:%M')} a {self.hora_cierre.strftime('%H:%M')}"
        return f"Excepción el {self.fecha}: Cerrado ({self.descripcion})"

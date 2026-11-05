from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import TenantAwareModel
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product
from apps.core.catalogs.models import Skill
# Asumimos que existirá un modelo TeamMember en un futuro módulo genérico
# from ..personal.models import TeamMember

class TourDetail(models.Model):
    """
    Detalles que convierten un Product en un Tour.
    """
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='tour_details'
    )
    required_skills = models.ManyToManyField(
        Skill,
        blank=True,
        help_text=_("Competencias requeridas para que un guía pueda realizar este tour.")
    )
    # Otros campos: duration_hours, difficulty_level, meeting_point, etc.

    def __str__(self):
        return f"Detalles de Tour para: {self.product.nombre}"

    class Meta:
        app_label = 'prestadores'

# class TeamMemberSkill(TenantAwareModel):
#     """
#     Tabla intermedia para asignar un Skill a un TeamMember, con fechas de validez.
#     """
#     team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='skills')
#     skill = models.ForeignKey(Skill, on_delete=models.PROTECT)
#     issue_date = models.DateField(null=True, blank=True)
#     expiry_date = models.DateField(null=True, blank=True)
#
#     class Meta:
#         unique_together = ('team_member', 'skill')

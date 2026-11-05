from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Skill, TourDetail
from .serializers import SkillSerializer
# Asumimos que TeamMember y su serializer existirán
# from ..personal.models import TeamMember
# from ..personal.serializers import TeamMemberSerializer
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.views import ProductViewSet

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

class TourProductViewSet(ProductViewSet):
    """
    Extiende el ProductViewSet para añadir lógica específica de tours.
    """
    @action(detail=True, methods=['get'], url_path='suggest-guides')
    def suggest_guides(self, request, pk=None):
        tour_product = self.get_object()
        try:
            required_skills = tour_product.tour_details.required_skills.all()

            # Lógica para encontrar guías que cumplan con los skills.
            # Esta es una simulación ya que TeamMember no existe aún.
            # guides = TeamMember.objects.filter(roles__name='Guía Turístico')
            # qualified_guides = []
            # for guide in guides:
            #     if required_skills.issubset(guide.skills.all()):
            #         qualified_guides.append(guide)

            # Por ahora, devolvemos una respuesta simulada
            return Response([
                {'id': 1, 'username': 'guia_calificado_1'},
                {'id': 2, 'username': 'guia_calificado_2'},
            ])

        except TourDetail.DoesNotExist:
            return Response({"error": "Este producto no es un tour configurable."}, status=status.HTTP_404_NOT_FOUND)

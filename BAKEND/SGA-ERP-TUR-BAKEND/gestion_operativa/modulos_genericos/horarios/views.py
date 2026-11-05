from rest_framework import viewsets, permissions
from .models import Horario, ExcepcionHorario
from .serializers import HorarioSerializer, ExcepcionHorarioSerializer
from apps.prestadores.mi_negocio.permissions import IsPrestadorOwner

class HorarioViewSet(viewsets.ModelViewSet):
    serializer_class = HorarioSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        return Horario.objects.filter(perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        serializer.save(perfil=self.request.user.perfil_prestador)

class ExcepcionHorarioViewSet(viewsets.ModelViewSet):
    serializer_class = ExcepcionHorarioSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        return ExcepcionHorario.objects.filter(perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        serializer.save(perfil=self.request.user.perfil_prestador)

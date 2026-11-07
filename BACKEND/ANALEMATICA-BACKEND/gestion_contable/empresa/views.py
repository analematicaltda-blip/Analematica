from rest_framework import viewsets, permissions
from .models import AdminCompany
from rest_framework import serializers
from apps.admin_plataforma.mixins import SystemicERPViewSetMixin
from api.permissions import IsSuperAdmin

class AdminCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminCompany
        fields = '__all__'

class AdminCompanyViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = AdminCompany.objects.all()
    serializer_class = AdminCompanySerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

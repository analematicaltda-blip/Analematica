from rest_framework import serializers
from ..models.divipola import Department, Municipality
from ..models.provider_models import TourismProvider

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['code', 'name']

class MunicipalitySerializer(serializers.ModelSerializer):
    dept_code = serializers.CharField(source='dept.code', read_only=True)
    dept_name = serializers.CharField(source='dept.name', read_only=True)

    class Meta:
        model = Municipality
        fields = ['code', 'name', 'dept_code', 'dept_name']

class TourismProviderSerializer(serializers.ModelSerializer):
    dept_code = serializers.CharField(source='divipola_dept.code', allow_blank=True)
    mun_code = serializers.CharField(source='divipola_mun.code', allow_blank=True)

    class Meta:
        model = TourismProvider
        fields = '__all__'

    def create(self, validated_data):
        dept_code = validated_data.pop('dept_code', None)
        mun_code = validated_data.pop('mun_code', None)
        instance = super().create(validated_data)
        if dept_code:
            dept = Department.objects.get(code=dept_code)
            instance.divipola_dept = dept
        if mun_code:
            mun = Municipality.objects.get(code=mun_code)
            instance.divipola_mun = mun
        instance.save()
        return instance


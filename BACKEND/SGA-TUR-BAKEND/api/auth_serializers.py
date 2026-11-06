from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from .models import CustomUser, Profile
from apps.turismo.models.divipola import Department, Municipality
from django.db import transaction

class LocationAwareRegisterSerializer(RegisterSerializer):
    username = None
    dept_code = serializers.CharField(max_length=2, required=True, write_only=True)
    mun_code = serializers.CharField(max_length=5, required=True, write_only=True)

    # RNT Optional but highly recommended for Via 2
    rnt_number = serializers.CharField(max_length=50, required=False, write_only=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data.pop('username', None)
        return data

    def validate(self, data):
        dept_code = data.get('dept_code')
        mun_code = data.get('mun_code')

        try:
            dept = Department.objects.get(code=dept_code)
            mun = Municipality.objects.get(code=mun_code, dept=dept)
        except Department.DoesNotExist:
            raise serializers.ValidationError({"dept_code": "Código de departamento inválido."})
        except Municipality.DoesNotExist:
            raise serializers.ValidationError({"mun_code": "Código de municipio inválido para este departamento."})

        data['department'] = dept
        data['municipality'] = mun
        return data

    @transaction.atomic
    def save(self, request):
        user = super().save(request)
        user.username = self.validated_data.get('email', '')
        user.save()

        # Sincronizar ubicación en el perfil
        Profile.objects.update_or_create(
            user=user,
            defaults={
                'department': self.validated_data['department'],
                'municipality': self.validated_data['municipality']
            }
        )

        # Si es un prestador, intentar validar RNT si se proveyó
        rnt_num = self.validated_data.get('rnt_number')
        if rnt_num:
            from apps.turismo.services.rnt_integration import RNTIntegrationService
            from apps.turismo.models.provider_models import TourismProvider

            # Buscamos o creamos el provider
            provider, _ = TourismProvider.objects.get_or_create(
                owner=user,
                defaults={
                    'name': f"Negocio de {user.get_full_name() or user.username}",
                    'department': self.validated_data['department'],
                    'municipality': self.validated_data['municipality'],
                    'rnt_number': rnt_num
                }
            )
            RNTIntegrationService.sync_provider(provider.id)

        return user

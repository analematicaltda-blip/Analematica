# SaritaUnificado/backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_genericos/perfil/serializers.py
from rest_framework import serializers
# Se corrige la importación para que apunte a los modelos locales del dominio.
from .models import ProviderProfile, CategoriaPrestador

class CategoriaPrestadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaPrestador
        fields = ['nombre', 'slug']

class PerfilSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo de Perfil del prestador.
    """
    # El campo 'categoria' ya no existe en el modelo ProviderProfile refactorizado.
    # Se debe eliminar o adaptar si se vuelve a añadir.
    # categoria = serializers.StringRelatedField()
    usuario = serializers.StringRelatedField()

    class Meta:
        model = ProviderProfile
        fields = [
            'id', 'usuario', 'nombre_comercial', 'provider_type', 'telefono_principal',
            'email_comercial', 'direccion', # 'categoria' eliminado
            'is_verified'
        ]
        read_only_fields = ['usuario', 'is_verified']

class PerfilUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar el perfil del prestador.
    Permite la actualización de campos específicos.
    """
    class Meta:
        model = ProviderProfile
        fields = [
            'nombre_comercial', 'telefono_principal', 'email_comercial',
            'direccion'
            # 'logo', 'sitio_web', 'redes_sociales' # Estos campos no existen en el modelo refactorizado
        ]

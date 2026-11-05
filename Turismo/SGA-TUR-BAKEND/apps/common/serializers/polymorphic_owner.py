
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

class PolymorphicOwnerSerializerMixin(serializers.Serializer):
    """
    Un mixin de serializer para manejar un campo 'owner' polimórfico.

    Serializa el owner a un diccionario: `{'type': 'app.ModelName', 'id': 123}`.
    Deserializa desde el mismo formato, validando y asignando los campos
    `owner_content_type` y `owner_object_id` en la instancia.
    """
    owner = serializers.JSONField(
        write_only=True,
        required=False,
        help_text='Diccionario con "type" (ej. "prestadores.providerprofile") y "id" del owner.'
    )
    owner_details = serializers.SerializerMethodField(source='get_owner', read_only=True)

    def get_owner_details(self, obj):
        if obj.owner:
            content_type = ContentType.objects.get_for_model(obj.owner)
            return {
                'type': f'{content_type.app_label}.{content_type.model}',
                'id': str(obj.owner.pk),
            }
        return None

    def create(self, validated_data):
        owner_data = validated_data.pop('owner', None)

        if owner_data:
            if isinstance(owner_data, dict):
                # Caso 1: El owner viene como un dict desde la API
                self._handle_owner_dict(owner_data, validated_data)
            else:
                # Caso 2: El owner viene como un objeto desde .save(owner=...)
                validated_data['owner'] = owner_data

        return super().create(validated_data)

    def update(self, instance, validated_data):
        owner_data = validated_data.pop('owner', None)

        if owner_data:
            if isinstance(owner_data, dict):
                self._handle_owner_dict(owner_data, validated_data)
            else:
                validated_data['owner'] = owner_data
        elif 'owner' in self.context['request'].data and self.context['request'].data.get('owner') is None:
             instance.owner = None

        return super().update(instance, validated_data)

    def _handle_owner_dict(self, owner_data, validated_data):
        try:
            owner_type_str = owner_data.get('type')
            owner_id = owner_data.get('id')

            if not owner_type_str or not owner_id:
                raise serializers.ValidationError("El campo 'owner' debe incluir 'type' y 'id'.")

            app_label, model_name = owner_type_str.split('.')
            owner_content_type = ContentType.objects.get(app_label=app_label, model=model_name)

            owner_model_class = owner_content_type.model_class()
            owner_instance = owner_model_class.objects.get(pk=owner_id)

            validated_data['owner_content_type'] = owner_content_type
            validated_data['owner_object_id'] = owner_id

        except ContentType.DoesNotExist:
            raise serializers.ValidationError(f"El tipo de owner '{owner_type_str}' no es válido.")
        except owner_model_class.DoesNotExist:
            raise serializers.ValidationError(f"El objeto owner con id '{owner_id}' no existe.")
        except Exception as e:
            raise serializers.ValidationError(f"Error procesando el owner: {e}")

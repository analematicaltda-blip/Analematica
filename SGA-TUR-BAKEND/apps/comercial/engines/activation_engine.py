import logging
import uuid
from ..models import Subscription
from apps.domain_business.operativa.models import ProviderProfile
from api.models import CustomUser

logger = logging.getLogger(__name__)

class ActivationEngine:
    """
    Motor de activación automática de infraestructura de cliente (Tenant).
    """

    @staticmethod
    def activate_tenant(subscription: Subscription, user_data: dict) -> bool:
        """
        Crea el perfil del prestador y configura sus límites.
        """
        try:
            # 1. Crear o recuperar usuario administrador
            user, created = CustomUser.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'username': user_data['email'],
                    'role': CustomUser.Role.PRESTADOR,
                    'first_name': user_data.get('name', 'Admin')
                }
            )

            if created:
                user.set_password(str(uuid.uuid4())) # Generar password temporal
                user.save()

            # 2. Crear Perfil de Prestador (Tenant)
            profile = ProviderProfile.objects.create(
                usuario=user,
                nombre_comercial=user_data.get('company_name', 'Nueva Empresa'),
                provider_type=user_data.get('provider_type', ProviderProfile.ProviderTypes.HOTEL),
                is_active=True,
                is_verified=True
            )

            # 3. Vincular suscripción al tenant real
            subscription.tenant_id = profile.id
            subscription.status = Subscription.Status.ACTIVE
            subscription.save()

            logger.info(f"Tenant ACTIVADO: {profile.nombre_comercial} (ID: {profile.id})")
            return True

        except Exception as e:
            logger.error(f"Fallo en activación de tenant: {str(e)}")
            return False

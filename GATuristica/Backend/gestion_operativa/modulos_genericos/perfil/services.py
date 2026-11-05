import logging
logger = logging.getLogger(__name__)
class PerfilService:
    @staticmethod
    def get_full_profile(perfil_id):
        from .models import ProviderProfile
        return ProviderProfile.objects.get(id=perfil_id)

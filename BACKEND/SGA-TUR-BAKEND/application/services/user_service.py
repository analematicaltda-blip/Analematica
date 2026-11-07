from infrastructure.repositories.user_repository import UserRepository
import logging

logger = logging.getLogger(__name__)

class UserService:
    """
    Capa de Aplicación para gestión de usuarios.
    Punto de contacto oficial para Agentes IA.
    """
    def __init__(self):
        self.repository = UserRepository()

    def get_user_profile(self, user_id):
        logger.info(f"UserService: Consultando perfil para {user_id}")
        user = self.repository.get_by_id(user_id)
        return {
            "id": str(user.id),
            "username": user.username,
            "role": user.role,
            "is_agent": user.is_agent
        }

    def promote_to_admin(self, user_id):
        logger.warning(f"UserService: Promocionando usuario {user_id} a ADMIN")
        return self.repository.update_role(user_id, "ADMIN")

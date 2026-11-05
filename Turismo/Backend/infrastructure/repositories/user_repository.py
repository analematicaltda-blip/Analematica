from django.shortcuts import get_object_or_404
from api.models import CustomUser

class UserRepository:
    """
    Encapsula el acceso a datos para usuarios y perfiles.
    """
    @staticmethod
    def get_by_id(user_id):
        return get_object_or_404(CustomUser, id=user_id)

    @staticmethod
    def filter_by_role(role):
        return CustomUser.objects.filter(role=role)

    @staticmethod
    def update_role(user_id, new_role):
        user = CustomUser.objects.get(id=user_id)
        user.role = new_role
        user.save()
        return user

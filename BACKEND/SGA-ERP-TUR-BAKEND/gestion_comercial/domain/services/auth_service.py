# domain/services/auth_service.py
from django.db import transaction
from infrastructure.models import User, Tenant, Role

def register_user(username, password, email, tenant_name):
    """
    Servicio de dominio para registrar un nuevo usuario y crear su tenant.
    """
    with transaction.atomic():
        # 1. Crear el Tenant
        if not tenant_name:
            tenant_name = f"{username}'s Organization"
        tenant = Tenant.objects.create(name=tenant_name)

        # 2. Crear el Usuario
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            tenant=tenant
        )

        # 3. (Opcional) Crear un rol de 'Admin' por defecto para el nuevo tenant
        admin_role = Role.objects.create(name='Admin', tenant=tenant)
        user.roles.add(admin_role)

        return user

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.schemas.tenancy import TenantCreate
from app.models.tenancy import Inquilino
from app.models.user import Usuario
from app.core.security import get_password_hash

def create_tenant_and_admin(db: Session, *, obj_in: TenantCreate) -> Inquilino:
    """
    Creates a new Tenant (Inquilino) and its initial admin user.
    This function handles the transaction for creating both records.
    """
    # Start a transaction
    with db.begin_nested():
        # 1. Create the Inquilino (Tenant)
        db_tenant = Inquilino(
            nombre_empresa=obj_in.nombre_empresa,
            tipo_organizacion=obj_in.tipo_organizacion,
            ambito_organizacional=obj_in.ambito_organizacional
        )
        db.add(db_tenant)
        db.flush() # Flush to get the ID for the new tenant

        # 2. Create the admin user for this tenant
        hashed_password = get_password_hash(obj_in.admin_password)
        # Use email prefix as username for simplicity
        admin_username = obj_in.admin_email.split('@')[0]

        db_admin = Usuario(
            nombre_usuario=admin_username,
            correo=obj_in.admin_email,
            password_hash=hashed_password,
            nombre_completo=obj_in.admin_nombre_completo,
            rol='admin_empresa', # Set the role name
            inquilino_id=db_tenant.id, # Link to the new tenant
            activo=True
        )
        db.add(db_admin)
        db.flush() # Flush to get the ID for the new admin

        # 3. Assign the 'admin_empresa' role in the user_roles table
        get_role_query = text("SELECT id FROM roles WHERE nombre = 'admin_empresa'")
        role_result = db.execute(get_role_query).fetchone()
        if not role_result:
            raise ValueError("Role 'admin_empresa' not found in 'roles' table.")

        role_id = role_result[0]

        assign_role_query = text(
            "INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"
        )
        db.execute(assign_role_query, {"user_id": db_admin.id, "role_id": role_id})

    # The transaction is committed here upon exiting the 'with' block
    # We need to refresh the tenant object to load relationships
    db.refresh(db_tenant)
    # Manually attach the admin for the response model
    db_tenant.admin = db_admin

    return db_tenant

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..models.user import Usuario, Role
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


def get_user_by_username(db: Session, username: str) -> Usuario | None:
    """
    Fetches a user from the database by their username.
    Populates role_list as a list of role name strings.
    """
    user = db.query(Usuario).filter(Usuario.nombre_usuario == username).first()
    if user:
        query = text("""
            SELECT r.nombre FROM roles r
            JOIN user_roles ur ON r.id = ur.role_id
            WHERE ur.user_id = :user_id
        """)
        roles_result = db.execute(query, {"user_id": user.id}).fetchall()
        role_names = [row[0] for row in roles_result]
        if not role_names and user.rol:
            role_names = [user.rol.value if hasattr(user.rol, 'value') else str(user.rol)]
        user.role_list = role_names
    return user


def get(db: Session, id: int) -> Usuario | None:
    """
    Fetches a user from the database by their ID.
    Populates role_list as a list of role name strings.
    """
    user = db.query(Usuario).filter(Usuario.id == id).first()
    if user:
        query = text("""
            SELECT r.nombre FROM roles r
            JOIN user_roles ur ON r.id = ur.role_id
            WHERE ur.user_id = :user_id
        """)
        roles_result = db.execute(query, {"user_id": user.id}).fetchall()
        role_names = [row[0] for row in roles_result]
        if not role_names and user.rol:
            role_names = [user.rol.value if hasattr(user.rol, 'value') else str(user.rol)]
        user.role_list = role_names
    return user


def create_user(db: Session, user: UserCreate) -> Usuario:
    """
    Creates a new user in the database and assigns them a role via ORM relationship.
    """
    hashed_password = get_password_hash(user.password)
    db_user = Usuario(
        nombre_usuario=user.nombre_usuario,
        correo=user.email,
        password_hash=hashed_password,
        nombre_completo=user.nombre_completo,
        rol=user.rol,
        inquilino_id=user.inquilino_id,
        activo=True
    )

    role_obj = db.query(Role).filter(Role.nombre == user.rol).first()
    if not role_obj:
        raise ValueError(f"Role '{user.rol}' not found in 'roles' table.")

    db_user.roles.append(role_obj)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    db_user.role_list = [user.rol]

    return db_user

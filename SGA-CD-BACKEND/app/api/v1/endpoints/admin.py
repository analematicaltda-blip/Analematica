from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app import schemas, crud
from app.models import user as user_model
from app.api import deps
from app.core.rate_limiter import rate_limit

router = APIRouter()


@router.get("/roles", response_model=List[str], summary="List all roles")
def get_all_roles(
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.role_required(["admin_general"]))
):
    """
    Get all available roles in the system.
    (Protected: admin_general only)
    """
    query = text("SELECT nombre FROM roles ORDER BY nombre")
    roles_result = db.execute(query).fetchall()
    return [row[0] for row in roles_result]


@router.get("/users/by-empresa", response_model=List[schemas.User], summary="List users by company", dependencies=[Depends(rate_limit("admin_users_by_empresa", max_requests=30, window_seconds=60))])
def get_users_by_empresa(
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.get_current_active_user)
):
    """
    Get all users belonging to the current user's empresa (inquilino).
    Accessible by roles that manage users within a company: admin_empresa, jefe_area, profesional_area, tecnico_area.
    """
    allowed_roles = {"admin_empresa", "jefe_area", "profesional_area", "tecnico_area", "admin_general"}
    user_roles = set(getattr(current_user, "role_codes", getattr(current_user, "role_list", [])))
    if not user_roles.intersection(allowed_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized. Requires one of the following roles: {list(allowed_roles)}",
        )

    users = db.query(user_model.Usuario).filter(
        user_model.Usuario.inquilino_id == current_user.inquilino_id
    ).all()

    for user in users:
        role_query = text("""
            SELECT r.nombre
            FROM roles r
            JOIN user_roles ur ON r.id = ur.role_id
            WHERE ur.user_id = :user_id
        """)
        roles_result = db.execute(role_query, {"user_id": user.id}).fetchall()
        role_names = [row[0] for row in roles_result]
        if not role_names and user.rol:
            role_names = [user.rol.value if hasattr(user.rol, 'value') else str(user.rol)]
        user.role_list = role_names

    return users


@router.post("/users/by-empresa", response_model=schemas.User, summary="Create user in company hierarchy")
def create_user_by_empresa(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user)
):
    """
    Enforces registration authority levels for company user creation:
    - Level 1 (admin_empresa): Can create jefe_area, profesional_area, tecnico_area.
    - Level 2 (jefe_area): Can create coordinador, profesor, almacenista, jefe_escenarios (responsable de espacios).
    - Level 3 (profesional_area, tecnico_area): Can prepare/create operativs (profesor, coordinador) within scope.
    No role can create a role with higher authority than itself.
    """
    if user_in.inquilino_id != current_user.inquilino_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create user for another tenant."
        )

    user_roles = set(getattr(current_user, "role_codes", getattr(current_user, "role_list", [])))

    # Whitelist estricta para la tríada operativa de área (jefe_area, profesional_area, tecnico_area)
    WHITELIST_OPERATIVA_AREA = {"profesor", "jefe_escenarios", "almacenista"}
    level_1_roles = {"admin_empresa", "admin_general"}
    operational_triad_roles = {"jefe_area", "profesional_area", "tecnico_area"}

    target_role = user_in.rol.strip()

    if user_roles.intersection(level_1_roles):
        allowed_target_roles = {
            "jefe_area", "profesional_area", "tecnico_area"
        }
        if target_role not in allowed_target_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{target_role}' cannot be created by your authority level."
            )
    elif "jefe_area" in user_roles:
        # jefe_area es Primer Jefe de Área y puede crear a su Segundo en Jefe (coordinador) y a la whitelist operativa
        allowed_jefe_targets = WHITELIST_OPERATIVA_AREA | {"coordinador"}
        if target_role not in allowed_jefe_targets:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Su rol como Jefe de Área solo tiene autorización para dar de alta a: coordinador, profesor, jefe_escenarios y almacenista."
            )
    elif user_roles.intersection({"profesional_area", "tecnico_area"}):
        if target_role not in WHITELIST_OPERATIVA_AREA:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Su rol operativo solo tiene autorización para dar de alta a: profesor, jefe_escenarios y almacenista."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role does not have authority to create new personnel."
        )

    # Check for existing user username or email
    existing_by_username = db.query(user_model.Usuario).filter(
        user_model.Usuario.nombre_usuario == user_in.nombre_usuario
    ).first()
    if existing_by_username:
        raise HTTPException(status_code=400, detail="Username already registered.")

    existing_by_email = db.query(user_model.Usuario).filter(
        user_model.Usuario.correo == user_in.email
    ).first()
    if existing_by_email:
        raise HTTPException(status_code=400, detail="Email address already registered.")

    new_user = crud.user.create_user(db=db, user=user_in)
    return new_user


@router.patch("/users/{user_id}/status", response_model=schemas.User, summary="Toggle user active status (Baja/Reactivacion)")
def toggle_user_status(
    user_id: int,
    active: bool,
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.get_current_active_user)
):
    """
    Toggle user active status.
    - admin_empresa / admin_general can toggle any user in tenant.
    - jefe_area can suspend / deactivate coordinadores and staff in their tenant.
    """
    user = db.query(user_model.Usuario).filter(
        user_model.Usuario.id == user_id,
        user_model.Usuario.inquilino_id == current_user.inquilino_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found in tenant.")

    user_roles = set(getattr(current_user, "role_codes", getattr(current_user, "role_list", [])))
    allowed_roles = {"admin_empresa", "admin_general", "jefe_area"}

    if not user_roles.intersection(allowed_roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to deactivate personnel.")

    user.activo = active
    db.add(user)
    db.commit()
    db.refresh(user)

    role_query = text("""
        SELECT r.nombre
        FROM roles r
        JOIN user_roles ur ON r.id = ur.role_id
        WHERE ur.user_id = :user_id
    """)
    roles_result = db.execute(role_query, {"user_id": user.id}).fetchall()
    role_names = [row[0] for row in roles_result]
    if not role_names and user.rol:
        role_names = [user.rol.value if hasattr(user.rol, 'value') else str(user.rol)]
    user.role_list = role_names

    return user


@router.get("/areas", response_model=List[schemas.area.Area], summary="List areas by company")
def get_areas_by_empresa(
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.get_current_active_user)
):
    """
    Get all areas belonging to the current user's empresa (inquilino).
    Accessible by admin_empresa.
    """
    # Role check
    user_roles = set(getattr(current_user, "role_codes", []))
    if "admin_empresa" not in user_roles and "admin_general" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Requires 'admin_empresa' or 'admin_general' role.",
        )

    areas = crud.area.get_areas_by_tenant(db=db, inquilino_id=current_user.inquilino_id)
    return areas


@router.get("/indicadores", summary="Get base institutional indicators for analytics dashboard")
def get_indicadores_institucionales(
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.get_current_active_user)
):
    """
    Returns unified base institutional indicators for the user's tenant:
    1. cantidad_instructores: Active teachers/instructors
    2. cantidad_alumnos_inscritos: Active enrolled students
    3. cantidad_alumnos_retirados: Inactive or withdrawn students
    4. alumnos_por_especialidad: Breakdown of active students per sport/cultural specialty
    """
    tenant_id = current_user.inquilino_id

    # 1. Active teachers count
    from app.models.user import Profesor, Alumno
    from app.models.academic import Inscripcion
    from app.models.catalog import CatalogoEspecialidad, EmpresaEspecialidad

    total_teachers = db.query(Profesor).filter(Profesor.inquilino_id == tenant_id).count()

    # 2. Total active students
    active_students_count = db.query(Alumno).join(user_model.Usuario).filter(
        Alumno.inquilino_id == tenant_id,
        user_model.Usuario.activo == True
    ).count()

    # 3. Total withdrawn students
    withdrawn_students_count = db.query(Alumno).join(user_model.Usuario).filter(
        Alumno.inquilino_id == tenant_id,
        user_model.Usuario.activo == False
    ).count()

    # 4. Breakdown of enrolled students per specialty
    # Query active enrollments grouped by specialty
    specialties_breakdown = []
    empresa_especialidades = db.query(EmpresaEspecialidad).filter(
        EmpresaEspecialidad.inquilino_id == tenant_id,
        EmpresaEspecialidad.activa == True
    ).all()

    for ee in empresa_especialidades:
        spec = db.query(CatalogoEspecialidad).filter(CatalogoEspecialidad.id == ee.especialidad_id).first()
        spec_name = spec.nombre if spec else f"Especialidad #{ee.especialidad_id}"
        spec_category = spec.categoria if spec else "General"

        # Count active enrollments for this specialty
        student_count = db.query(Inscripcion).filter(
            Inscripcion.inquilino_id == tenant_id,
            Inscripcion.especialidad_id == ee.especialidad_id,
            Inscripcion.estado == "activa"
        ).count()

        specialties_breakdown.append({
            "especialidad_id": ee.especialidad_id,
            "nombre": spec_name,
            "categoria": spec_category,
            "alumnos_inscritos": student_count
        })

    return {
        "inquilino_id": tenant_id,
        "cantidad_instructores": total_teachers,
        "cantidad_alumnos_inscritos": active_students_count,
        "cantidad_alumnos_retirados": withdrawn_students_count,
        "alumnos_por_especialidad": specialties_breakdown
    }
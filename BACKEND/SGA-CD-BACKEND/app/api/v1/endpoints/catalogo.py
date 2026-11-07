import re
import html
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app import models
from app.api import deps
from app.models.catalog import CatalogoEspecialidad, EmpresaEspecialidad, ProfesorEspecialidad
from app.models.tenancy import Inquilino
from app.core.catalogo_data import CATALOGO_OFICIAL

router = APIRouter()


# --- Pydantic Schemas ---
class CustomSpecialtyCreate(BaseModel):
    vertical: str = Field(..., description="'deporte' o 'cultura'")
    nombre: str = Field(..., min_length=2, max_length=200)
    categoria: Optional[str] = Field(default="Personalizada", max_length=100)

class AdoptSpecialtiesRequest(BaseModel):
    especialidad_ids: List[int]

class UpdateVocacionRequest(BaseModel):
    vocacion_institucional: str = Field(..., description="'deportiva' o 'cultural'")

class AssignTeacherSpecialtyRequest(BaseModel):
    empresa_especialidad_id: int
    nivel_academico: Optional[str] = Field(None, max_length=100)
    certificacion_avalada: bool = False

class UpdateTeacherAvalRequest(BaseModel):
    certificacion_avalada: bool
    nivel_academico: Optional[str] = Field(None, max_length=100)


def seed_catalogo_if_empty(db: Session):
    """Seed the 1,000 official master specialties into catalogo_especialidades if empty."""
    try:
        count = db.query(func.count(CatalogoEspecialidad.id)).scalar()
        if not isinstance(count, int):
            count = 0
    except Exception:
        count = 0

    if count < 1000:
        existing_codes = set(
            row[0] for row in db.query(CatalogoEspecialidad.codigo_canonico).all()
        )
        items_to_insert = []
        for item in CATALOGO_OFICIAL:
            if item["codigo_canonico"] not in existing_codes:
                items_to_insert.append(
                    CatalogoEspecialidad(
                        vertical=item["vertical"],
                        categoria=item["categoria"],
                        codigo_canonico=item["codigo_canonico"],
                        nombre=item["nombre"],
                        es_estandar=True,
                        activo=True,
                    )
                )
        if items_to_insert:
            db.bulk_save_objects(items_to_insert)
            db.commit()


def sanitize_text(text: str) -> str:
    """Sanitizes text against XSS and script injection."""
    text = html.escape(text.strip())
    # Remove any stray tags or dangerous characters
    clean = re.sub(r'<[^>]*>', '', text)
    return clean


@router.get("/especialidades")
def search_catalogo_especialidades(
    vertical: Optional[str] = Query(None, description="'deporte' o 'cultura'"),
    search: Optional[str] = Query(None, description="Texto de búsqueda"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    """
    Search master catalog specialties by vertical and keyword.
    Automatically seeds official catalog on first run.
    """
    seed_catalogo_if_empty(db)

    query = db.query(CatalogoEspecialidad).filter(CatalogoEspecialidad.activo == True)

    if vertical:
        clean_v = vertical.strip().lower()
        if clean_v in ("deporte", "deportiva"):
            query = query.filter(CatalogoEspecialidad.vertical == "deporte")
        elif clean_v in ("cultura", "cultural"):
            query = query.filter(CatalogoEspecialidad.vertical == "cultura")

    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(CatalogoEspecialidad.nombre).like(term),
                func.lower(CatalogoEspecialidad.categoria).like(term),
            )
        )

    results = query.order_by(CatalogoEspecialidad.nombre.asc()).limit(limit).all()

    return [
        {
            "id": r.id,
            "vertical": r.vertical,
            "categoria": r.categoria,
            "codigo_canonico": r.codigo_canonico,
            "nombre": r.nombre,
            "es_estandar": r.es_estandar,
        }
        for r in results
    ]


@router.post("/especialidades/custom", status_code=status.HTTP_201_CREATED)
def create_custom_especialidad_on_the_fly(
    payload: CustomSpecialtyCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    """
    On-The-Fly specialty creation and tenant adoption mechanism.
    Sanitizes input, checks for existing match (case/trim insensitive),
    creates master entry if new (es_estandar=False), and associates with tenant.
    """
    if not current_user.inquilino_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no tiene una organización asociada."
        )

    clean_nombre = sanitize_text(payload.nombre)
    if not clean_nombre or len(clean_nombre) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de especialidad inválido."
        )

    clean_vertical = payload.vertical.strip().lower()
    if clean_vertical in ("deportiva", "deporte"):
        vertical_val = "deporte"
    elif clean_vertical in ("cultural", "cultura"):
        vertical_val = "cultura"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vertical debe ser 'deporte' o 'cultura'."
        )

    clean_cat = sanitize_text(payload.categoria or "Personalizada")

    seed_catalogo_if_empty(db)

    # 1. Search existing (case-insensitive & trimmed)
    existing_spec = (
        db.query(CatalogoEspecialidad)
        .filter(
            CatalogoEspecialidad.vertical == vertical_val,
            func.lower(func.trim(CatalogoEspecialidad.nombre)) == clean_nombre.lower(),
        )
        .first()
    )

    if not existing_spec:
        # Create new master specialty entry
        canon_code = f"custom_{vertical_val[:3]}_{current_user.inquilino_id}_{re.sub(r'[^a-z0-9]+', '_', clean_nombre.lower())[:30]}"
        existing_spec = CatalogoEspecialidad(
            vertical=vertical_val,
            categoria=clean_cat,
            codigo_canonico=canon_code,
            nombre=clean_nombre,
            es_estandar=False,
            creado_por_inquilino_id=current_user.inquilino_id,
            activo=True,
        )
        db.add(existing_spec)
        db.commit()
        db.refresh(existing_spec)

    # 2. Associate with tenant in empresa_especialidades if not already associated
    empresa_assoc = (
        db.query(EmpresaEspecialidad)
        .filter(
            EmpresaEspecialidad.inquilino_id == current_user.inquilino_id,
            EmpresaEspecialidad.especialidad_id == existing_spec.id,
        )
        .first()
    )

    if not empresa_assoc:
        empresa_assoc = EmpresaEspecialidad(
            inquilino_id=current_user.inquilino_id,
            especialidad_id=existing_spec.id,
            activa=True,
        )
        db.add(empresa_assoc)
        db.commit()
        db.refresh(empresa_assoc)
    elif not empresa_assoc.activa:
        empresa_assoc.activa = True
        db.commit()

    return {
        "id": empresa_assoc.id,
        "inquilino_id": empresa_assoc.inquilino_id,
        "especialidad_id": existing_spec.id,
        "nombre": existing_spec.nombre,
        "vertical": existing_spec.vertical,
        "categoria": existing_spec.categoria,
        "es_estandar": existing_spec.es_estandar,
        "activa": empresa_assoc.activa,
        "fecha_adopcion": empresa_assoc.fecha_adopcion,
    }


@router.get("/my-specialties")
def get_my_company_specialties(
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    """Get all active adopted specialties for the authenticated user's organization."""
    if not current_user.inquilino_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario sin organización asignada."
        )

    assocs = (
        db.query(EmpresaEspecialidad)
        .join(CatalogoEspecialidad, EmpresaEspecialidad.especialidad_id == CatalogoEspecialidad.id)
        .filter(
            EmpresaEspecialidad.inquilino_id == current_user.inquilino_id,
            EmpresaEspecialidad.activa == True,
        )
        .order_by(CatalogoEspecialidad.nombre.asc())
        .all()
    )

    return [
        {
            "empresa_especialidad_id": a.id,
            "especialidad_id": a.especialidad.id,
            "nombre": a.especialidad.nombre,
            "vertical": a.especialidad.vertical,
            "categoria": a.especialidad.categoria,
            "es_estandar": a.especialidad.es_estandar,
            "fecha_adopcion": a.fecha_adopcion,
        }
        for a in assocs
    ]


@router.post("/my-specialties/adopt")
def adopt_company_specialties(
    payload: AdoptSpecialtiesRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    """Adopt multiple existing catalog specialties by ID for current tenant."""
    if not current_user.inquilino_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario sin organización asignada."
        )

    adopted = []
    for spec_id in payload.especialidad_ids:
        spec = db.query(CatalogoEspecialidad).filter(CatalogoEspecialidad.id == spec_id).first()
        if not spec:
            continue

        assoc = (
            db.query(EmpresaEspecialidad)
            .filter(
                EmpresaEspecialidad.inquilino_id == current_user.inquilino_id,
                EmpresaEspecialidad.especialidad_id == spec_id,
            )
            .first()
        )

        if not assoc:
            assoc = EmpresaEspecialidad(
                inquilino_id=current_user.inquilino_id,
                especialidad_id=spec_id,
                activa=True,
            )
            db.add(assoc)
            db.commit()
            db.refresh(assoc)
        elif not assoc.activa:
            assoc.activa = True
            db.commit()

        adopted.append(
            {
                "empresa_especialidad_id": assoc.id,
                "especialidad_id": spec.id,
                "nombre": spec.nombre,
                "vertical": spec.vertical,
            }
        )

    return {"message": "Especialidades adoptadas exitosamente", "adopted": adopted}


@router.delete("/my-specialties/{especialidad_id}")
def unadopt_company_specialty(
    especialidad_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    """Unadopt a specialty for the current tenant."""
    if not current_user.inquilino_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario sin organización asignada."
        )

    assoc = (
        db.query(EmpresaEspecialidad)
        .filter(
            EmpresaEspecialidad.inquilino_id == current_user.inquilino_id,
            EmpresaEspecialidad.especialidad_id == especialidad_id,
        )
        .first()
    )

    if not assoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Especialidad no adoptada por la organización."
        )

    assoc.activa = False
    db.commit()

    return {"message": "Especialidad removida de la organización"}


@router.patch("/vocacion")
def update_tenant_vocacion(
    payload: UpdateVocacionRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    """Update tenant's institutional vocation ('deportiva' | 'cultural')."""
    if not current_user.inquilino_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario sin organización asignada."
        )

    clean_v = payload.vocacion_institucional.strip().lower()
    if clean_v not in ("deportiva", "cultural"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vocación debe ser 'deportiva' o 'cultural'."
        )

    tenant = db.query(Inquilino).filter(Inquilino.id == current_user.inquilino_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Organización no encontrada.")

    tenant.vocacion_institucional = clean_v
    db.commit()

    return {
        "inquilino_id": tenant.id,
        "nombre_empresa": tenant.nombre_empresa,
        "vocacion_institucional": tenant.vocacion_institucional,
    }


# --- Teacher Specialties & Aval Management ---

@router.get("/teachers/{teacher_id}/specialties")
def get_teacher_specialties(
    teacher_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    """
    Get all assigned specialties and institutional aval status for a specific teacher/instructor.
    Validates tenant isolation.
    """
    if not current_user.inquilino_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario sin organización asignada."
        )

    teacher = db.query(models.Usuario).filter(
        models.Usuario.id == teacher_id,
        models.Usuario.inquilino_id == current_user.inquilino_id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Docente o instructor no encontrado en su organización."
        )

    assocs = (
        db.query(ProfesorEspecialidad)
        .join(EmpresaEspecialidad, ProfesorEspecialidad.empresa_especialidad_id == EmpresaEspecialidad.id)
        .join(CatalogoEspecialidad, EmpresaEspecialidad.especialidad_id == CatalogoEspecialidad.id)
        .filter(
            ProfesorEspecialidad.usuario_id == teacher_id,
            EmpresaEspecialidad.inquilino_id == current_user.inquilino_id,
            EmpresaEspecialidad.activa == True
        )
        .all()
    )

    return [
        {
            "profesor_especialidad_id": a.id,
            "usuario_id": a.usuario_id,
            "empresa_especialidad_id": a.empresa_especialidad_id,
            "especialidad_id": a.empresa_especialidad.especialidad.id,
            "nombre": a.empresa_especialidad.especialidad.nombre,
            "vertical": a.empresa_especialidad.especialidad.vertical,
            "categoria": a.empresa_especialidad.especialidad.categoria,
            "certificacion_avalada": a.certificacion_avalada,
            "nivel_academico": a.nivel_academico,
            "estado_aval": "Avalado por la entidad" if a.certificacion_avalada else "Pendiente de revisión"
        }
        for a in assocs
    ]


@router.post("/teachers/{teacher_id}/specialties", status_code=status.HTTP_201_CREATED)
def assign_specialty_to_teacher(
    teacher_id: int,
    payload: AssignTeacherSpecialtyRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    """
    Assign an adopted company specialty to a teacher/instructor with tenant isolation.
    """
    if not current_user.inquilino_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario sin organización asignada."
        )

    # 1. Validate teacher exists and belongs to current tenant
    teacher = db.query(models.Usuario).filter(
        models.Usuario.id == teacher_id,
        models.Usuario.inquilino_id == current_user.inquilino_id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Docente o instructor no encontrado en su organización."
        )

    # 2. Validate empresa_especialidad exists, is active, and belongs to current tenant
    emp_spec = db.query(EmpresaEspecialidad).filter(
        EmpresaEspecialidad.id == payload.empresa_especialidad_id,
        EmpresaEspecialidad.inquilino_id == current_user.inquilino_id,
        EmpresaEspecialidad.activa == True
    ).first()

    if not emp_spec:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La especialidad seleccionada no está activa o no está adoptada por su organización."
        )

    # 3. Check for duplicate assignment
    existing_assoc = db.query(ProfesorEspecialidad).filter(
        ProfesorEspecialidad.usuario_id == teacher_id,
        ProfesorEspecialidad.empresa_especialidad_id == payload.empresa_especialidad_id
    ).first()

    if existing_assoc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El docente ya tiene asignada esta especialidad en su organización."
        )

    # 4. Create association
    new_assoc = ProfesorEspecialidad(
        usuario_id=teacher_id,
        empresa_especialidad_id=payload.empresa_especialidad_id,
        certificacion_avalada=payload.certificacion_avalada,
        nivel_academico=sanitize_text(payload.nivel_academico) if payload.nivel_academico else "Licenciatura / Profesional"
    )
    db.add(new_assoc)
    db.commit()
    db.refresh(new_assoc)

    return {
        "profesor_especialidad_id": new_assoc.id,
        "usuario_id": new_assoc.usuario_id,
        "empresa_especialidad_id": new_assoc.empresa_especialidad_id,
        "especialidad_nombre": emp_spec.especialidad.nombre,
        "vertical": emp_spec.especialidad.vertical,
        "certificacion_avalada": new_assoc.certificacion_avalada,
        "nivel_academico": new_assoc.nivel_academico,
        "estado_aval": "Avalado por la entidad" if new_assoc.certificacion_avalada else "Pendiente de revisión"
    }


@router.delete("/teachers/{teacher_id}/specialties/{profesor_especialidad_id}")
def remove_specialty_from_teacher(
    teacher_id: int,
    profesor_especialidad_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    """
    Remove a specialty assignment from a teacher/instructor with tenant isolation.
    """
    if not current_user.inquilino_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario sin organización asignada."
        )

    assoc = (
        db.query(ProfesorEspecialidad)
        .join(EmpresaEspecialidad, ProfesorEspecialidad.empresa_especialidad_id == EmpresaEspecialidad.id)
        .filter(
            ProfesorEspecialidad.id == profesor_especialidad_id,
            ProfesorEspecialidad.usuario_id == teacher_id,
            EmpresaEspecialidad.inquilino_id == current_user.inquilino_id
        )
        .first()
    )

    if not assoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación de especialidad no encontrada para este docente."
        )

    db.delete(assoc)
    db.commit()

    return {"message": "Asignación de especialidad removida exitosamente."}


@router.patch("/teachers/{teacher_id}/specialties/{profesor_especialidad_id}/aval")
def update_teacher_specialty_aval(
    teacher_id: int,
    profesor_especialidad_id: int,
    payload: UpdateTeacherAvalRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.Usuario = Depends(deps.get_current_active_user),
):
    """
    Update institutional aval status and academic level for a teacher's assigned specialty.
    Requires admin_empresa or admin_general role.
    """
    allowed_roles = {"admin_empresa", "admin_general", "jefe_area"}
    user_roles = set(getattr(current_user, "role_codes", []))
    if not user_roles and current_user.rol:
        role_val = current_user.rol.value if hasattr(current_user.rol, 'value') else str(current_user.rol)
        user_roles.add(role_val)
    if not user_roles.intersection(allowed_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado. Requiere rol de administración de empresa."
        )

    assoc = (
        db.query(ProfesorEspecialidad)
        .join(EmpresaEspecialidad, ProfesorEspecialidad.empresa_especialidad_id == EmpresaEspecialidad.id)
        .filter(
            ProfesorEspecialidad.id == profesor_especialidad_id,
            ProfesorEspecialidad.usuario_id == teacher_id,
            EmpresaEspecialidad.inquilino_id == current_user.inquilino_id
        )
        .first()
    )

    if not assoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación de especialidad no encontrada para este docente."
        )

    assoc.certificacion_avalada = payload.certificacion_avalada
    if payload.nivel_academico is not None:
        assoc.nivel_academico = sanitize_text(payload.nivel_academico)

    db.commit()
    db.refresh(assoc)

    return {
        "profesor_especialidad_id": assoc.id,
        "usuario_id": assoc.usuario_id,
        "certificacion_avalada": assoc.certificacion_avalada,
        "nivel_academico": assoc.nivel_academico,
        "estado_aval": "Avalado por la entidad" if assoc.certificacion_avalada else "No avalado / Pendiente"
    }

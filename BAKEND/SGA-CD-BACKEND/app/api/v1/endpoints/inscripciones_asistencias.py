from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.models import user as user_model
from app.models.academic import Clase
from app.models.catalog import EmpresaEspecialidad, ProfesorEspecialidad

router = APIRouter()

# --- Inscripcion Endpoints ---

@router.get("/inscripciones/clase/{clase_id}", response_model=List[schemas.Inscripcion])
def read_inscripciones_by_clase(
    clase_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve enrollments for a specific class with tenant validation.
    """
    clase = crud.clase.get_clase(db, clase_id=clase_id)
    if not clase or getattr(clase, "inquilino_id", current_user.inquilino_id) != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    inscripciones = crud.inscripcion_asistencia.get_inscripciones_by_clase(db, clase_id=clase_id)
    return inscripciones

@router.post("/inscripciones/", response_model=schemas.Inscripcion)
def create_inscripcion(
    *,
    db: Session = Depends(deps.get_db),
    inscripcion_in: schemas.InscripcionCreate,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new enrollment with tenant validation and teacher coverage enforcement.
    Rule: Enrollment is blocked if the class has no instructor assigned or if the assigned instructor
    does not have an active, institutionally avalado specialty for this organization.
    """
    if getattr(inscripcion_in, "inquilino_id", current_user.inquilino_id) != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create enrollment for another tenant.")

    # Teacher coverage check
    if inscripcion_in.clase_id:
        clase = db.query(Clase).filter(
            Clase.id == inscripcion_in.clase_id,
            Clase.inquilino_id == current_user.inquilino_id
        ).first()

        if not clase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La clase especificada no existe en su organización.")

        if not clase.instructor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se permite la matrícula: La especialidad o clase no tiene un instructor o formador asignado."
            )

        # Check if instructor is active and has an avalado specialty for this tenant matching class specialty
        query = (
            db.query(ProfesorEspecialidad)
            .join(EmpresaEspecialidad, ProfesorEspecialidad.empresa_especialidad_id == EmpresaEspecialidad.id)
            .join(user_model.Usuario, ProfesorEspecialidad.usuario_id == user_model.Usuario.id)
            .filter(
                ProfesorEspecialidad.usuario_id == clase.instructor_id,
                user_model.Usuario.activo == True,
                EmpresaEspecialidad.inquilino_id == current_user.inquilino_id,
                ProfesorEspecialidad.certificacion_avalada == True,
                EmpresaEspecialidad.activa == True
            )
        )

        clase_empresa_spec_id = getattr(clase, "empresa_especialidad_id", None)
        clase_spec_id = getattr(clase, "especialidad_id", None)

        if clase_empresa_spec_id:
            query = query.filter(ProfesorEspecialidad.empresa_especialidad_id == clase_empresa_spec_id)
        elif clase_spec_id:
            query = query.filter(EmpresaEspecialidad.especialidad_id == clase_spec_id)

        has_aval = query.first()

        if not has_aval:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se permite la matrícula: El instructor asignado no cuenta con el aval institucional habilitado para esta especialidad."
            )

    inscripcion = crud.inscripcion_asistencia.create_inscripcion(db=db, obj_in=inscripcion_in)
    return inscripcion

# --- Asistencia Endpoints ---

@router.get("/asistencias/clase/{clase_id}", response_model=List[schemas.Asistencia])
def read_asistencias_by_clase(
    clase_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve attendance for a specific class with tenant validation.
    """
    clase = crud.clase.get_clase(db, clase_id=clase_id)
    if not clase or getattr(clase, "inquilino_id", current_user.inquilino_id) != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    asistencias = crud.inscripcion_asistencia.get_asistencias_by_clase(db, clase_id=clase_id)
    return asistencias

@router.post("/asistencias/", response_model=schemas.Asistencia)
def create_asistencia(
    *,
    db: Session = Depends(deps.get_db),
    asistencia_in: schemas.AsistenciaCreate,
    current_user: user_model.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Log attendance for a student in a class with tenant validation.
    """
    if getattr(asistencia_in, "inquilino_id", current_user.inquilino_id) != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot log attendance for another tenant.")

    asistencia = crud.inscripcion_asistencia.create_asistencia(db=db, obj_in=asistencia_in)
    return asistencia

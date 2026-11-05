from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, crud
from app.models import user as user_model
from app.api import deps

router = APIRouter()

@router.get("/courses", response_model=List[schemas.clase.Clase], summary="List all courses for the current professor")
def get_my_courses(
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.role_required(["profesor"]))
):
    """
    Get all courses assigned to the currently logged-in professor for their tenant.
    (Protected: profesor only)
    """
    courses = crud.clase.get_clases_by_profesor(db=db, profesor_id=current_user.id)
    # Ensure tenant isolation
    tenant_courses = [c for c in courses if getattr(c, "inquilino_id", current_user.inquilino_id) == current_user.inquilino_id]
    return tenant_courses


@router.get("/courses/{course_id}/students", response_model=List[schemas.user.User], summary="List all students in a specific course")
def get_students_in_course(
    course_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.role_required(["profesor"]))
):
    """
    Get all students enrolled in a specific course.
    A professor can only view students for courses they teach in their own tenant.
    """
    # Verify the professor teaches this course and tenant matches
    course = crud.clase.get_clase(db=db, clase_id=course_id)
    if not course or getattr(course, "inquilino_id", current_user.inquilino_id) != current_user.inquilino_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    if course.profesor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view students for this course")

    students = crud.inscripcion_asistencia.get_alumnos_by_clase(db=db, clase_id=course_id)
    return students

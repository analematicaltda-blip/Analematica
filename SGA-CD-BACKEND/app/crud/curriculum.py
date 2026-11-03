from sqlalchemy.orm import Session
from typing import List

from ..models.curriculum import PlanCurricular, PlanCurricularTema
from app.schemas.curriculum import PlanCurricularCreate, PlanCurricularUpdate, PlanCurricularTemaCreate, PlanCurricularTemaUpdate

# --- CRUD for PlanCurricular ---

def get_plan(db: Session, plan_id: int) -> PlanCurricular | None:
    return db.query(PlanCurricular).filter(PlanCurricular.id == plan_id).first()

def get_planes_by_tenant(
    db: Session, *, inquilino_id: int, skip: int = 0, limit: int = 100
) -> List[PlanCurricular]:
    return (
        db.query(PlanCurricular)
        .filter(PlanCurricular.inquilino_id == inquilino_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_plan(db: Session, *, obj_in: PlanCurricularCreate) -> PlanCurricular:
    db_obj = PlanCurricular(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- CRUD for PlanCurricularTema ---

def create_tema(db: Session, *, obj_in: PlanCurricularTemaCreate) -> PlanCurricularTema:
    db_obj = PlanCurricularTema(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

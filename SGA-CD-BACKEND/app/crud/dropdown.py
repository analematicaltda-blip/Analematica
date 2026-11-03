from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..models.base import Base

# Define custom types for SQLAlchemy model and Pydantic schemas
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        Generic CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi_by_tenant(
        self, db: Session, *, inquilino_id: int, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return (
            db.query(self.model)
            .filter(self.model.inquilino_id == inquilino_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

# Import all dropdown models and schemas to create CRUD instances
from ..models import dropdowns
from app.schemas import dropdown

# Create a dictionary to hold all the CRUD objects
crud_dropdowns = {
    "generos": CRUDBase[dropdowns.Genero, dropdown.DropdownCreate, dropdown.DropdownUpdate](dropdowns.Genero),
    "grupos_etarios": CRUDBase[dropdowns.GrupoEtario, dropdown.DropdownCreate, dropdown.DropdownUpdate](dropdowns.GrupoEtario),
    "tipos_documento": CRUDBase[dropdowns.TipoDocumento, dropdown.DropdownCreate, dropdown.DropdownUpdate](dropdowns.TipoDocumento),
    "escolaridades": CRUDBase[dropdowns.Escolaridad, dropdown.DropdownCreate, dropdown.DropdownUpdate](dropdowns.Escolaridad),
    "discapacidades": CRUDBase[dropdowns.Discapacidad, dropdown.DropdownCreate, dropdown.DropdownUpdate](dropdowns.Discapacidad),
    "grupos_poblacionales": CRUDBase[dropdowns.GrupoPoblacional, dropdown.DropdownCreate, dropdown.DropdownUpdate](dropdowns.GrupoPoblacional),
    "barrios": CRUDBase[dropdowns.Barrio, dropdown.DropdownCreate, dropdown.DropdownUpdate](dropdowns.Barrio),
    "veredas": CRUDBase[dropdowns.Vereda, dropdown.DropdownCreate, dropdown.DropdownUpdate](dropdowns.Vereda),
    "resguardos": CRUDBase[dropdowns.Resguardo, dropdown.DropdownCreate, dropdown.DropdownUpdate](dropdowns.Resguardo),
    "tipos_escenario": CRUDBase[dropdowns.TipoEscenario, dropdown.DropdownCreate, dropdown.DropdownUpdate](dropdowns.TipoEscenario),
}

"""Additive install: keep legacy enrollments intact, seed canonical catalogs only if missing."""
import app.models
from app.models.institutional import InstitutionalProcess,EnrollmentEvent
from app.models.catalog import CatalogoEspecialidad
from app.models.user import Role,RolesEnum
from app.models.area import Area
from app.core.catalogo_data import CATALOGO_OFICIAL
from app.db.session import engine,SessionLocal

def install():
    assert {kind:sum(row['vertical']==kind for row in CATALOGO_OFICIAL) for kind in ['deporte','cultura']}=={'deporte':500,'cultura':500}
    for model in [InstitutionalProcess,EnrollmentEvent]:model.__table__.create(engine,checkfirst=True)
    with SessionLocal() as db:
        codes={row[0] for row in db.query(CatalogoEspecialidad.codigo_canonico).all()}
        names={(row.vertical,row.nombre.strip().lower()) for row in db.query(CatalogoEspecialidad).all()}
        for item in CATALOGO_OFICIAL:
            if item['codigo_canonico'] not in codes and (item['vertical'],item['nombre'].strip().lower()) not in names:
                db.add(CatalogoEspecialidad(**item,activo=True));codes.add(item['codigo_canonico']);names.add((item['vertical'],item['nombre'].strip().lower()))
        for role in RolesEnum:
            if not db.query(Role).filter_by(nombre=role.value).first():db.add(Role(nombre=role.value))
        for name in ['Deportes','Cultura']:
            if not db.query(Area).filter_by(nombre=name).first():db.add(Area(nombre=name))
        db.commit()
    print('Analítica institucional preparada; catálogo oficial 500 + 500 preservado. No se infirieron estados de inscripción ni se borraron datos.')
if __name__=='__main__':install()

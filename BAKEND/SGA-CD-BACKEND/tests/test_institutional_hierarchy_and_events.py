import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from app.models.base import Base
from app.models.user import Usuario, Role, Profesor, Alumno, RolesEnum
from app.models.tenancy import Inquilino
from app.models.catalog import CatalogoEspecialidad, EmpresaEspecialidad
from app.models.academic import Inscripcion
from app.schemas.user import UserCreate
from app.schemas.evento import EventoCreate, EventoParticipanteCreate
from app.api.v1.endpoints.admin import create_user_by_empresa, get_indicadores_institucionales
from app.api.v1.endpoints.eventos import create_evento, add_participante_to_evento

class TestInstitutionalHierarchyAndEvents(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()

        # Seed roles
        for r_enum in RolesEnum:
            role_obj = Role()
            role_obj.nombre = r_enum.value
            role_obj.descripcion = r_enum.value
            self.db.add(role_obj)
        self.db.commit()

        # Seed Tenant
        self.tenant = Inquilino()
        self.tenant.id = 100
        self.tenant.nombre_empresa = "Instituto Municipal de Deportes"
        self.tenant.vocacion_institucional = "deportiva"
        self.db.add(self.tenant)
        self.db.commit()

        # Seed Admin Empresa (Level 1)
        self.admin_user = Usuario()
        self.admin_user.id = 1
        self.admin_user.inquilino_id = 100
        self.admin_user.nombre_usuario = "admin_empresa_100"
        self.admin_user.correo = "admin@deportes.gov.co"
        self.admin_user.password_hash = "hash"
        self.admin_user.rol = RolesEnum.admin_empresa
        self.admin_user.activo = True
        self.admin_user.role_list = ["admin_empresa"]
        self.db.add(self.admin_user)

        # Seed Jefe Area (Level 2)
        self.jefe_user = Usuario()
        self.jefe_user.id = 2
        self.jefe_user.inquilino_id = 100
        self.jefe_user.nombre_usuario = "jefe_area_100"
        self.jefe_user.correo = "jefe@deportes.gov.co"
        self.jefe_user.password_hash = "hash"
        self.jefe_user.rol = RolesEnum.jefe_area
        self.jefe_user.activo = True
        self.jefe_user.role_list = ["jefe_area"]
        self.db.add(self.jefe_user)

        # Seed Profesional Area (Level 3 - No Direct Creation Authority)
        self.profesional_user = Usuario()
        self.profesional_user.id = 3
        self.profesional_user.inquilino_id = 100
        self.profesional_user.nombre_usuario = "profesional_100"
        self.profesional_user.correo = "profesional@deportes.gov.co"
        self.profesional_user.password_hash = "hash"
        self.profesional_user.rol = RolesEnum.profesional_area
        self.profesional_user.activo = True
        self.profesional_user.role_list = ["profesional_area"]
        self.db.add(self.profesional_user)

        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_01_admin_creates_jefe_area_success(self):
        user_in = UserCreate(
            email="jefe2@deportes.gov.co",
            nombre_usuario="jefe_area_2",
            password="Password123!",
            rol="jefe_area",
            inquilino_id=100,
            nombre_completo="Jefe Area 2"
        )
        new_user = create_user_by_empresa(db=self.db, user_in=user_in, current_user=self.admin_user)
        self.assertIsNotNone(new_user.id)
        self.assertEqual(new_user.rol, RolesEnum.jefe_area)

    def test_02_jefe_area_cannot_create_admin_empresa(self):
        user_in = UserCreate(
            email="admin2@deportes.gov.co",
            nombre_usuario="admin_empresa_2",
            password="Password123!",
            rol="admin_empresa",
            inquilino_id=100,
            nombre_completo="Admin Illegal"
        )
        with self.assertRaises(HTTPException) as ctx:
            create_user_by_empresa(db=self.db, user_in=user_in, current_user=self.jefe_user)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_02b_profesional_area_can_create_whitelisted_users(self):
        user_in = UserCreate(
            email="profesor1@deportes.gov.co",
            nombre_usuario="profesor_1",
            password="Password123!",
            rol="profesor",
            inquilino_id=100,
            nombre_completo="Profesor Uno"
        )
        new_user = create_user_by_empresa(db=self.db, user_in=user_in, current_user=self.profesional_user)
        self.assertIsNotNone(new_user.id)
        self.assertEqual(new_user.rol, RolesEnum.profesor)

    def test_02c_profesional_area_cannot_create_forbidden_users(self):
        user_in = UserCreate(
            email="coord1@deportes.gov.co",
            nombre_usuario="coordinador_1",
            password="Password123!",
            rol="coordinador",
            inquilino_id=100,
            nombre_completo="Coordinador Uno"
        )
        with self.assertRaises(HTTPException) as ctx:
            create_user_by_empresa(db=self.db, user_in=user_in, current_user=self.profesional_user)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_03_create_evento_and_check_authority(self):
        evento_in = EventoCreate(
            nombre="Torneo Municipal de Judo",
            descripcion="Competencia oficial",
            tipo="evento",
            alcance="municipal",
            area="Deportes",
            inquilino_id=100,
            creado_por_usuario_id=2
        )
        evt = create_evento(db=self.db, evento_in=evento_in, current_user=self.jefe_user)
        self.assertEqual(evt.nombre, "Torneo Municipal de Judo")

    def test_04_institutional_indicators(self):
        ind = get_indicadores_institucionales(db=self.db, current_user=self.admin_user)
        self.assertEqual(ind["inquilino_id"], 100)
        self.assertIn("cantidad_instructores", ind)
        self.assertIn("cantidad_alumnos_inscritos", ind)
        self.assertIn("cantidad_alumnos_retirados", ind)
        self.assertIn("alumnos_por_especialidad", ind)

if __name__ == "__main__":
    unittest.main()

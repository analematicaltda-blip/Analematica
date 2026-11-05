import unittest
from starlette.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.deps import get_db
from app.models.base import Base
from app.models.tenancy import Inquilino
from app.models.user import Usuario, RolesEnum
from app.models.catalog import CatalogoEspecialidad, EmpresaEspecialidad, ProfesorEspecialidad
from app.core.security import create_access_token

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_teacher_spec.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


class TestTeacherSpecialties(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._old_override = app.dependency_overrides.get(get_db)
        app.dependency_overrides[get_db] = override_get_db
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        cls.db = TestingSessionLocal()

        # Create Tenant A & B
        cls.tenant_a = Inquilino(nombre_empresa="Tenant A Sports", vocacion_institucional="deportiva")
        cls.tenant_b = Inquilino(nombre_empresa="Tenant B Culture", vocacion_institucional="cultural")
        cls.db.add_all([cls.tenant_a, cls.tenant_b])
        cls.db.commit()

        # Create Admin A and Teachers A1, A2
        cls.admin_a = Usuario(
            nombre_usuario="admin_a",
            correo="admin_a@test.com",
            password_hash="hash",
            rol=RolesEnum.admin_empresa,
            inquilino_id=cls.tenant_a.id,
            activo=True
        )
        cls.teacher_a1 = Usuario(
            nombre_usuario="teacher_a1",
            correo="teacher_a1@test.com",
            password_hash="hash",
            rol=RolesEnum.profesor,
            inquilino_id=cls.tenant_a.id,
            activo=True
        )
        cls.teacher_a2 = Usuario(
            nombre_usuario="teacher_a2",
            correo="teacher_a2@test.com",
            password_hash="hash",
            rol=RolesEnum.profesor,
            inquilino_id=cls.tenant_a.id,
            activo=True
        )

        # Create Teacher B
        cls.teacher_b = Usuario(
            nombre_usuario="teacher_b",
            correo="teacher_b@test.com",
            password_hash="hash",
            rol=RolesEnum.profesor,
            inquilino_id=cls.tenant_b.id,
            activo=True
        )

        cls.db.add_all([cls.admin_a, cls.teacher_a1, cls.teacher_a2, cls.teacher_b])
        cls.db.commit()

        # Create Master Catalog Specialties
        cls.spec1 = CatalogoEspecialidad(vertical="deporte", categoria="Conjunto", codigo_canonico="dep_tkd", nombre="Taekwondo", es_estandar=True, activo=True)
        cls.spec2 = CatalogoEspecialidad(vertical="deporte", categoria="Individual", codigo_canonico="dep_fut", nombre="Fútbol", es_estandar=True, activo=True)
        cls.spec3 = CatalogoEspecialidad(vertical="cultura", categoria="Danza", codigo_canonico="cul_jor", nombre="Joropo", es_estandar=True, activo=True)
        cls.db.add_all([cls.spec1, cls.spec2, cls.spec3])
        cls.db.commit()

        # Adopt Specialties for Tenant A
        cls.emp_spec_a1 = EmpresaEspecialidad(inquilino_id=cls.tenant_a.id, especialidad_id=cls.spec1.id, activa=True)
        cls.emp_spec_a2 = EmpresaEspecialidad(inquilino_id=cls.tenant_a.id, especialidad_id=cls.spec2.id, activa=True)
        # Adopt Specialty for Tenant B
        cls.emp_spec_b1 = EmpresaEspecialidad(inquilino_id=cls.tenant_b.id, especialidad_id=cls.spec3.id, activa=True)

        cls.db.add_all([cls.emp_spec_a1, cls.emp_spec_a2, cls.emp_spec_b1])
        cls.db.commit()

        # Tokens
        cls.token_admin_a = create_access_token(data={"sub": str(cls.admin_a.id), "roles": ["admin_empresa"]})
        cls.token_teacher_b = create_access_token(data={"sub": str(cls.teacher_b.id), "roles": ["profesor"]})

        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        Base.metadata.drop_all(bind=engine)
        if getattr(cls, "_old_override", None) is not None:
            app.dependency_overrides[get_db] = cls._old_override
        else:
            from app.api.deps import get_db as deps_get_db
            from tests.conftest import override_get_db as conf_override
            app.dependency_overrides[deps_get_db] = conf_override

    def test_assign_and_list_teacher_specialties(self):
        # 1. Assign Spec A1 to Teacher A1
        res = self.client.post(
            f"/api/v1/catalogo/teachers/{self.teacher_a1.id}/specialties",
            json={"empresa_especialidad_id": self.emp_spec_a1.id, "nivel_academico": "Licenciatura en Educación Física", "certificacion_avalada": True},
            headers={"Authorization": f"Bearer {self.token_admin_a}"}
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["especialidad_nombre"], "Taekwondo")
        self.assertTrue(data["certificacion_avalada"])

        # 2. Assign Spec A2 to Teacher A1 (Multiple specialties for one teacher)
        res2 = self.client.post(
            f"/api/v1/catalogo/teachers/{self.teacher_a1.id}/specialties",
            json={"empresa_especialidad_id": self.emp_spec_a2.id, "nivel_academico": "Entrenador Nacional"},
            headers={"Authorization": f"Bearer {self.token_admin_a}"}
        )
        self.assertEqual(res2.status_code, 201)

        # 3. Assign Spec A1 to Teacher A2 (Multiple teachers for one specialty)
        res3 = self.client.post(
            f"/api/v1/catalogo/teachers/{self.teacher_a2.id}/specialties",
            json={"empresa_especialidad_id": self.emp_spec_a1.id, "nivel_academico": "Instructor Cinturón Negro", "certificacion_avalada": True},
            headers={"Authorization": f"Bearer {self.token_admin_a}"}
        )
        self.assertEqual(res3.status_code, 201)

        # 4. List Teacher A1 Specialties
        res_list = self.client.get(
            f"/api/v1/catalogo/teachers/{self.teacher_a1.id}/specialties",
            headers={"Authorization": f"Bearer {self.token_admin_a}"}
        )
        self.assertEqual(res_list.status_code, 200)
        specs = res_list.json()
        self.assertEqual(len(specs), 2)

    def test_duplicate_and_tenant_isolation(self):
        # 1. Duplicate assignment rejection
        res_dup = self.client.post(
            f"/api/v1/catalogo/teachers/{self.teacher_a1.id}/specialties",
            json={"empresa_especialidad_id": self.emp_spec_a1.id},
            headers={"Authorization": f"Bearer {self.token_admin_a}"}
        )
        self.assertEqual(res_dup.status_code, 400)

        # 2. Cross-tenant assignment attempt (Admin A trying to assign Tenant B's specialty)
        res_cross = self.client.post(
            f"/api/v1/catalogo/teachers/{self.teacher_a1.id}/specialties",
            json={"empresa_especialidad_id": self.emp_spec_b1.id},
            headers={"Authorization": f"Bearer {self.token_admin_a}"}
        )
        self.assertEqual(res_cross.status_code, 400)

        # 3. Cross-tenant teacher access attempt (Tenant B trying to access Teacher A1)
        res_cross_get = self.client.get(
            f"/api/v1/catalogo/teachers/{self.teacher_a1.id}/specialties",
            headers={"Authorization": f"Bearer {self.token_teacher_b}"}
        )
        self.assertEqual(res_cross_get.status_code, 404)

    def test_update_aval_status(self):
        # List teacher A1 specs
        specs = self.client.get(
            f"/api/v1/catalogo/teachers/{self.teacher_a1.id}/specialties",
            headers={"Authorization": f"Bearer {self.token_admin_a}"}
        ).json()

        target = specs[1] # Spec A2 (not avalada yet)

        # Patch aval status
        res_aval = self.client.patch(
            f"/api/v1/catalogo/teachers/{self.teacher_a1.id}/specialties/{target['profesor_especialidad_id']}/aval",
            json={"certificacion_avalada": True, "nivel_academico": "Magíster en Ciencias del Deporte"},
            headers={"Authorization": f"Bearer {self.token_admin_a}"}
        )
        self.assertEqual(res_aval.status_code, 200)
        self.assertTrue(res_aval.json()["certificacion_avalada"])
        self.assertEqual(res_aval.json()["nivel_academico"], "Magíster en Ciencias del Deporte")


if __name__ == "__main__":
    unittest.main()

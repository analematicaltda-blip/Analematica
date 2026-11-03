import unittest
from starlette.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.deps import get_db
from app.models.base import Base
from app.models.tenancy import Inquilino
from app.models.user import Usuario, RolesEnum
from app.models.academic import Clase, ProcesoFormacion
from app.models.catalog import CatalogoEspecialidad, EmpresaEspecialidad, ProfesorEspecialidad
from app.core.security import create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_enrollment_coverage.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


class TestEnrollmentCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._old_override = app.dependency_overrides.get(get_db)
        app.dependency_overrides[get_db] = override_get_db
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        cls.db = TestingSessionLocal()

        # Create Tenant
        cls.tenant = Inquilino(nombre_empresa="Sports Institute", vocacion_institucional="deportiva")
        cls.db.add(cls.tenant)
        cls.db.commit()

        # Create Admin & Teacher Users
        cls.admin = Usuario(nombre_usuario="admin_cov", correo="admin_cov@test.com", password_hash="h", rol=RolesEnum.admin_empresa, inquilino_id=cls.tenant.id, activo=True)
        cls.teacher = Usuario(nombre_usuario="teacher_cov", correo="teacher_cov@test.com", password_hash="h", rol=RolesEnum.profesor, inquilino_id=cls.tenant.id, activo=True)
        cls.db.add_all([cls.admin, cls.teacher])
        cls.db.commit()

        # Create Process & Classes
        cls.proceso = ProcesoFormacion(inquilino_id=cls.tenant.id, nombre_proceso="Proceso Taekwondo", tipo_proceso="Formación")
        cls.db.add(cls.proceso)
        cls.db.commit()

        # Class 1: No instructor
        cls.clase_no_teacher = Clase(inquilino_id=cls.tenant.id, nombre_clase="Taekwondo Básico - Sin Profe", proceso_id=cls.proceso.id, instructor_id=None, area="Deportes")
        # Class 2: Has instructor but no aval
        cls.clase_no_aval = Clase(inquilino_id=cls.tenant.id, nombre_clase="Taekwondo Intermedio - Sin Aval", proceso_id=cls.proceso.id, instructor_id=cls.teacher.id, area="Deportes")
        # Class 3: Has instructor with aval
        cls.clase_with_aval = Clase(inquilino_id=cls.tenant.id, nombre_clase="Taekwondo Avanzado - Con Aval", proceso_id=cls.proceso.id, instructor_id=cls.teacher.id, area="Deportes")

        cls.db.add_all([cls.clase_no_teacher, cls.clase_no_aval, cls.clase_with_aval])
        cls.db.commit()

        # Specialty & Adoption
        cls.spec = CatalogoEspecialidad(vertical="deporte", categoria="Combate", codigo_canonico="dep_tkd_cov", nombre="Taekwondo Coverage", es_estandar=True, activo=True)
        cls.db.add(cls.spec)
        cls.db.commit()

        cls.emp_spec = EmpresaEspecialidad(inquilino_id=cls.tenant.id, especialidad_id=cls.spec.id, activa=True)
        cls.db.add(cls.emp_spec)
        cls.db.commit()

        # Assign specialty to teacher with certificacion_avalada = True for Class 3 testing later
        cls.prof_spec = ProfesorEspecialidad(usuario_id=cls.teacher.id, empresa_especialidad_id=cls.emp_spec.id, certificacion_avalada=False, nivel_academico="Licenciado")
        cls.db.add(cls.prof_spec)
        cls.db.commit()

        cls.token_admin = create_access_token(data={"sub": str(cls.admin.id), "roles": ["admin_empresa"]})
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

    def test_enrollment_blocking(self):
        # 1. Attempt enrollment in class with no instructor -> Reject HTTP 400
        res1 = self.client.post(
            "/api/v1/academic/inscripciones/",
            json={"clase_id": self.clase_no_teacher.id, "inquilino_id": self.tenant.id, "alumno_id": 1, "area": "Deportes", "fecha_inscripcion": "2025-10-23T10:00:00Z"},
            headers={"Authorization": f"Bearer {self.token_admin}"}
        )
        self.assertEqual(res1.status_code, 400)
        self.assertIn("no tiene un instructor", res1.json()["detail"])

        # 2. Attempt enrollment in class with instructor but no aval -> Reject HTTP 400
        res2 = self.client.post(
            "/api/v1/academic/inscripciones/",
            json={"clase_id": self.clase_no_aval.id, "inquilino_id": self.tenant.id, "alumno_id": 1, "area": "Deportes", "fecha_inscripcion": "2025-10-23T10:00:00Z"},
            headers={"Authorization": f"Bearer {self.token_admin}"}
        )
        self.assertEqual(res2.status_code, 400)
        self.assertIn("no cuenta con el aval institucional", res2.json()["detail"])

        # 3. Grant institutional aval to teacher
        self.prof_spec.certificacion_avalada = True
        self.db.commit()

        # 4. Attempt enrollment in class with avalado instructor -> Success
        res3 = self.client.post(
            "/api/v1/academic/inscripciones/",
            json={"clase_id": self.clase_with_aval.id, "inquilino_id": self.tenant.id, "alumno_id": 1, "area": "Deportes", "fecha_inscripcion": "2025-10-23T10:00:00Z"},
            headers={"Authorization": f"Bearer {self.token_admin}"}
        )
        self.assertEqual(res3.status_code, 200)

    def test_negative_cases(self):
        # A. Inactive instructor -> Reject HTTP 400
        self.teacher.activo = False
        self.db.commit()

        res_inact = self.client.post(
            "/api/v1/academic/inscripciones/",
            json={"clase_id": self.clase_with_aval.id, "inquilino_id": self.tenant.id, "alumno_id": 1, "area": "Deportes", "fecha_inscripcion": "2025-10-23T10:00:00Z"},
            headers={"Authorization": f"Bearer {self.token_admin}"}
        )
        self.assertEqual(res_inact.status_code, 400)

        # Restore active teacher
        self.teacher.activo = True
        self.db.commit()

        # B. Inactive tenant specialty adoption -> Reject HTTP 400
        self.emp_spec.activa = False
        self.db.commit()

        res_spec_inact = self.client.post(
            "/api/v1/academic/inscripciones/",
            json={"clase_id": self.clase_with_aval.id, "inquilino_id": self.tenant.id, "alumno_id": 1, "area": "Deportes", "fecha_inscripcion": "2025-10-23T10:00:00Z"},
            headers={"Authorization": f"Bearer {self.token_admin}"}
        )
        self.assertEqual(res_spec_inact.status_code, 400)

        # Restore active specialty adoption
        self.emp_spec.activa = True
        self.db.commit()

        # C. Cross-tenant class enrollment -> Reject HTTP 403 Forbidden
        res_cross = self.client.post(
            "/api/v1/academic/inscripciones/",
            json={"clase_id": self.clase_with_aval.id, "inquilino_id": 9999, "alumno_id": 1, "area": "Deportes", "fecha_inscripcion": "2025-10-23T10:00:00Z"},
            headers={"Authorization": f"Bearer {self.token_admin}"}
        )
        self.assertEqual(res_cross.status_code, 403)


if __name__ == "__main__":
    unittest.main()

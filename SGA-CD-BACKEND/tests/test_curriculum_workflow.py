import unittest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException, status

from app.models.base import Base
from app.models.user import Usuario, Role, RolesEnum
from app.models.tenancy import Inquilino
from app.models.curriculum import PlanCurricular
from app.schemas.curriculum import PlanCurricularCreate, PlanCurricularUpdate, PlanCurricularReviewAction
from app.api.v1.endpoints.curriculum import (
    create_plan,
    update_plan,
    presentar_plan_revision,
    vobo_tecnico_coordinador,
    devolver_plan_observaciones,
    ratificar_plan_jefe_area
)

class TestCurriculumApprovalWorkflow(unittest.TestCase):

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

        # Seed Tenants (Plan Básico and Plan Full)
        self.tenant_a = Inquilino(id=100, nombre_empresa="IMDER Villavicencio", plan="basico")
        self.tenant_b = Inquilino(id=200, nombre_empresa="Club Deportivo B", plan="full")
        self.db.add_all([self.tenant_a, self.tenant_b])
        self.db.commit()

        # Users for Tenant A
        self.profesor_a1 = Usuario(id=1, inquilino_id=100, nombre_usuario="prof_a1", correo="prof1@a.com", password_hash="hash", rol=RolesEnum.profesor)
        self.profesor_a1.role_codes = ["profesor"]
        self.profesor_a2 = Usuario(id=2, inquilino_id=100, nombre_usuario="prof_a2", correo="prof2@a.com", password_hash="hash", rol=RolesEnum.profesor)
        self.profesor_a2.role_codes = ["profesor"]
        self.coord_a = Usuario(id=3, inquilino_id=100, nombre_usuario="coord_a", correo="coord@a.com", password_hash="hash", rol=RolesEnum.coordinador)
        self.coord_a.role_codes = ["coordinador"]
        self.jefe_a = Usuario(id=4, inquilino_id=100, nombre_usuario="jefe_a", correo="jefe@a.com", password_hash="hash", rol=RolesEnum.jefe_area)
        self.jefe_a.role_codes = ["jefe_area"]
        self.admin_empresa_a = Usuario(id=5, inquilino_id=100, nombre_usuario="admin_emp_a", correo="admin@a.com", password_hash="hash", rol=RolesEnum.admin_empresa)
        self.admin_empresa_a.role_codes = ["admin_empresa"]

        # Users for Tenant B
        self.profesor_b = Usuario(id=6, inquilino_id=200, nombre_usuario="prof_b", correo="prof@b.com", password_hash="hash", rol=RolesEnum.profesor)
        self.profesor_b.role_codes = ["profesor"]

        self.db.add_all([self.profesor_a1, self.profesor_a2, self.coord_a, self.jefe_a, self.admin_empresa_a, self.profesor_b])
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_01_authorized_professor_presents_own_plan(self):
        plan_in = PlanCurricularCreate(
            nombre_plan="Plan Anual de Taekwondo 52 Semanas",
            descripcion="Plan de entrenamiento 2024-2025",
            area="Deportes",
            inquilino_id=100,
            creado_por_usuario_id=1
        )
        plan = create_plan(db=self.db, plan_in=plan_in, current_user=self.profesor_a1)
        self.assertEqual(plan.estado_aprobacion, "borrador")

        plan = presentar_plan_revision(plan_id=plan.id, db=self.db, current_user=self.profesor_a1)
        self.assertEqual(plan.estado_aprobacion, "en_revision")

    def test_02_unauthorized_user_cannot_present_foreign_plan(self):
        plan_in = PlanCurricularCreate(
            nombre_plan="Plan Anual de Natación 52 Semanas",
            area="Deportes",
            inquilino_id=100,
            creado_por_usuario_id=1
        )
        plan = create_plan(db=self.db, plan_in=plan_in, current_user=self.profesor_a1)

        # Another profesor cannot submit
        with self.assertRaises(HTTPException) as ctx:
            presentar_plan_revision(plan_id=plan.id, db=self.db, current_user=self.profesor_a2)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_03_only_authorized_coordinator_can_grant_vobo(self):
        plan_in = PlanCurricularCreate(
            nombre_plan="Plan de Gimnasia 52 Semanas",
            area="Deportes",
            inquilino_id=100,
            creado_por_usuario_id=1
        )
        plan = create_plan(db=self.db, plan_in=plan_in, current_user=self.profesor_a1)
        presentar_plan_revision(plan_id=plan.id, db=self.db, current_user=self.profesor_a1)

        # Profesor cannot grant VoBo
        with self.assertRaises(HTTPException) as ctx:
            vobo_tecnico_coordinador(plan_id=plan.id, db=self.db, current_user=self.profesor_a1)
        self.assertEqual(ctx.exception.status_code, 403)

        # Coordinator grants VoBo
        action = PlanCurricularReviewAction(observaciones="VoBo técnico otorgado.")
        plan = vobo_tecnico_coordinador(plan_id=plan.id, action=action, db=self.db, current_user=self.coord_a)
        self.assertEqual(plan.estado_aprobacion, "vobo_tecnico")

    def test_04_returns_require_mandatory_observations(self):
        plan_in = PlanCurricularCreate(
            nombre_plan="Plan de Baloncesto 52 Semanas",
            area="Deportes",
            inquilino_id=100,
            creado_por_usuario_id=1
        )
        plan = create_plan(db=self.db, plan_in=plan_in, current_user=self.profesor_a1)
        presentar_plan_revision(plan_id=plan.id, db=self.db, current_user=self.profesor_a1)

        # Empty observations raises 400
        empty_action = PlanCurricularReviewAction(observaciones="")
        with self.assertRaises(HTTPException) as ctx:
            devolver_plan_observaciones(plan_id=plan.id, action=empty_action, db=self.db, current_user=self.coord_a)
        self.assertEqual(ctx.exception.status_code, 400)

        # Valid observations succeeds
        valid_action = PlanCurricularReviewAction(observaciones="Revisar semana 14.")
        plan = devolver_plan_observaciones(plan_id=plan.id, action=valid_action, db=self.db, current_user=self.coord_a)
        self.assertEqual(plan.estado_aprobacion, "devuelto")
        self.assertEqual(plan.observaciones_revision, "Revisar semana 14.")

    def test_05_only_jefe_area_can_ratify_after_vobo(self):
        plan_in = PlanCurricularCreate(
            nombre_plan="Plan de Danza 52 Semanas",
            area="Cultura",
            inquilino_id=100,
            creado_por_usuario_id=1
        )
        plan = create_plan(db=self.db, plan_in=plan_in, current_user=self.profesor_a1)
        presentar_plan_revision(plan_id=plan.id, db=self.db, current_user=self.profesor_a1)

        # Cannot ratify before VoBo
        with self.assertRaises(HTTPException) as ctx:
            ratificar_plan_jefe_area(plan_id=plan.id, db=self.db, current_user=self.jefe_a)
        self.assertEqual(ctx.exception.status_code, 400)

        vobo_tecnico_coordinador(plan_id=plan.id, db=self.db, current_user=self.coord_a)

        # Coordinator cannot ratify
        with self.assertRaises(HTTPException) as ctx:
            ratificar_plan_jefe_area(plan_id=plan.id, db=self.db, current_user=self.coord_a)
        self.assertEqual(ctx.exception.status_code, 403)

        # Jefe de área ratifies
        plan = ratificar_plan_jefe_area(plan_id=plan.id, db=self.db, current_user=self.jefe_a)
        self.assertEqual(plan.estado_aprobacion, "aprobado_definitivo")

    def test_06_admin_empresa_cannot_execute_reserved_transitions(self):
        plan_in = PlanCurricularCreate(
            nombre_plan="Plan de Escultura 52 Semanas",
            area="Cultura",
            inquilino_id=100,
            creado_por_usuario_id=1
        )
        plan = create_plan(db=self.db, plan_in=plan_in, current_user=self.profesor_a1)

        # admin_empresa cannot present
        with self.assertRaises(HTTPException) as ctx:
            presentar_plan_revision(plan_id=plan.id, db=self.db, current_user=self.admin_empresa_a)
        self.assertEqual(ctx.exception.status_code, 403)

        presentar_plan_revision(plan_id=plan.id, db=self.db, current_user=self.profesor_a1)

        # admin_empresa cannot grant VoBo
        with self.assertRaises(HTTPException) as ctx:
            vobo_tecnico_coordinador(plan_id=plan.id, db=self.db, current_user=self.admin_empresa_a)
        self.assertEqual(ctx.exception.status_code, 403)

        vobo_tecnico_coordinador(plan_id=plan.id, db=self.db, current_user=self.coord_a)

        # admin_empresa cannot ratify
        with self.assertRaises(HTTPException) as ctx:
            ratificar_plan_jefe_area(plan_id=plan.id, db=self.db, current_user=self.admin_empresa_a)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_07_cross_tenant_isolation_maintained(self):
        plan_in = PlanCurricularCreate(
            nombre_plan="Plan Inquilino B",
            area="Deportes",
            inquilino_id=200,
            creado_por_usuario_id=6
        )
        plan_b = create_plan(db=self.db, plan_in=plan_in, current_user=self.profesor_b)

        with self.assertRaises(HTTPException) as ctx:
            presentar_plan_revision(plan_id=plan_b.id, db=self.db, current_user=self.profesor_a1)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_08_editing_approved_plan_reopens_flow_and_increments_version(self):
        plan_in = PlanCurricularCreate(
            nombre_plan="Plan de Atletismo 52 Semanas",
            area="Deportes",
            inquilino_id=100,
            creado_por_usuario_id=1
        )
        plan = create_plan(db=self.db, plan_in=plan_in, current_user=self.profesor_a1)
        presentar_plan_revision(plan_id=plan.id, db=self.db, current_user=self.profesor_a1)
        vobo_tecnico_coordinador(plan_id=plan.id, db=self.db, current_user=self.coord_a)
        ratificar_plan_jefe_area(plan_id=plan.id, db=self.db, current_user=self.jefe_a)
        self.assertEqual(plan.estado_aprobacion, "aprobado_definitivo")

        # Edit approved plan
        update_in = PlanCurricularUpdate(nombre_plan="Plan Atletismo v2", area="Deportes")
        plan = update_plan(plan_id=plan.id, plan_in=update_in, db=self.db, current_user=self.profesor_a1)
        self.assertEqual(plan.estado_aprobacion, "borrador")
        self.assertEqual(plan.version, 2)

    def test_09_basic_and_full_plans_maintain_curriculum_access(self):
        # Tenant A (Plan Básico)
        plan_a_in = PlanCurricularCreate(nombre_plan="Plan Básico", area="Deportes", inquilino_id=100, creado_por_usuario_id=1)
        plan_a = create_plan(db=self.db, plan_in=plan_a_in, current_user=self.profesor_a1)
        self.assertIsNotNone(plan_a.id)

        # Tenant B (Plan Full)
        plan_b_in = PlanCurricularCreate(nombre_plan="Plan Full", area="Cultura", inquilino_id=200, creado_por_usuario_id=6)
        plan_b = create_plan(db=self.db, plan_in=plan_b_in, current_user=self.profesor_b)
        self.assertIsNotNone(plan_b.id)

if __name__ == "__main__":
    unittest.main()

"""
Automated Endpoint Tests for GET /api/v1/tenants/my-plan-capabilities (Phase 8.13.3-B1).

Verifies tenant capability resolution endpoint, authentication checks, inactive tenant denial,
expired subscription handling, tenant isolation, parameter manipulation rejection,
absence of API secrets in response payload, and read-only non-mutating execution.
"""
import sys
import unittest
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta

try:
    import fastapi
except ImportError:
    pass

try:
    import sqlalchemy
except ImportError:
    pass

try:
    import pydantic
except ImportError:
    pass

try:
    import pydantic_settings
except ImportError:
    pass

# Force reload of tenancy endpoint to bind decorated functions properly
if "app.api.v1.endpoints.tenancy" in sys.modules:
    del sys.modules["app.api.v1.endpoints.tenancy"]
if "app.services.plan_capability_service" in sys.modules:
    del sys.modules["app.services.plan_capability_service"]

from fastapi import HTTPException, status
from app.api.v1.endpoints.tenancy import get_my_plan_capabilities


class DummyEntity:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def setup_db_mock(db_session, tenant_obj, sub_obj=None):
    def query_handler(model):
        q_mock = MagicMock()
        model_str = str(model)
        model_name = getattr(model, "__name__", model_str)
        if "Inquilino" in model_name or "Inquilino" in model_str:
            q_mock.filter.return_value.first.return_value = tenant_obj
            q_mock.filter.return_value.order_by.return_value.first.return_value = tenant_obj
        elif "Suscripcion" in model_name or "Suscripcion" in model_str:
            q_mock.filter.return_value.first.return_value = sub_obj
            q_mock.filter.return_value.order_by.return_value.first.return_value = sub_obj
        else:
            q_mock.filter.return_value.first.return_value = None
            q_mock.filter.return_value.order_by.return_value.first.return_value = None
        return q_mock
    db_session.query.side_effect = query_handler


class TestTenancyCapabilitiesEndpoint(unittest.TestCase):

    def setUp(self):
        self.db_session = MagicMock()

    def test_1_authenticated_basic_plan_user(self):
        """1. Usuario autenticado con Plan Básico."""
        user = DummyEntity(id=1, inquilino_id=10, nombre_usuario="admin_local", activo=True)
        tenant = DummyEntity(
            id=10,
            nombre_empresa="IMDER Villavicencio",
            tipo_organizacion="entidad_publica",
            ambito_organizacional="municipal",
            plan="basico",
            activo=True
        )
        sub = DummyEntity(id=1, inquilino_id=10, plan="basico", estado="activa")

        setup_db_mock(self.db_session, tenant, sub)

        caps_dict = get_my_plan_capabilities(db=self.db_session, current_user=user)

        self.assertEqual(caps_dict["inquilino_id"], 10)
        self.assertEqual(caps_dict["canonical_plan"], "basico")
        self.assertTrue(caps_dict["is_active"])
        self.assertTrue(caps_dict["panel_institucional_enabled"])
        self.assertFalse(caps_dict["crm_leads_enabled"])
        self.assertFalse(caps_dict["ai_images_enabled"])
        self.assertEqual(caps_dict["monthly_limits"]["images"], 0)

    def test_2_authenticated_full_plan_user(self):
        """2. Usuario autenticado con Plan Full."""
        user = DummyEntity(id=2, inquilino_id=20, nombre_usuario="admin_meta", activo=True)
        tenant = DummyEntity(
            id=20,
            nombre_empresa="Gobernación del Meta",
            tipo_organizacion="entidad_publica",
            ambito_organizacional="departamental",
            plan="pro_anual",
            activo=True
        )
        sub = DummyEntity(id=2, inquilino_id=20, plan="pro_anual", estado="activa")

        setup_db_mock(self.db_session, tenant, sub)

        caps_dict = get_my_plan_capabilities(db=self.db_session, current_user=user)

        self.assertEqual(caps_dict["inquilino_id"], 20)
        self.assertEqual(caps_dict["canonical_plan"], "full")
        self.assertTrue(caps_dict["is_active"])
        self.assertTrue(caps_dict["crm_leads_enabled"])
        self.assertTrue(caps_dict["ai_images_enabled"])
        self.assertEqual(caps_dict["monthly_limits"]["images"], 100)
        self.assertEqual(caps_dict["monthly_limits"]["llm_prompts"], 500)

    def test_3_user_without_associated_tenant(self):
        """3. Usuario sin inquilino asociado."""
        user = DummyEntity(id=3, inquilino_id=None, nombre_usuario="orphan_user", activo=True)

        with self.assertRaises(HTTPException) as cm:
            get_my_plan_capabilities(db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not associated", cm.exception.detail)

    def test_4_inactive_tenant(self):
        """4. Inquilino inactivo."""
        user = DummyEntity(id=4, inquilino_id=40, nombre_usuario="admin_inactive", activo=True)
        tenant = DummyEntity(id=40, nombre_empresa="Empresa Inactiva", activo=False)

        setup_db_mock(self.db_session, tenant, None)

        with self.assertRaises(HTTPException) as cm:
            get_my_plan_capabilities(db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("inactive", cm.exception.detail)

    def test_5_expired_or_canceled_subscription(self):
        """5. Suscripción vencida o cancelada."""
        user = DummyEntity(id=5, inquilino_id=50, nombre_usuario="admin_expired", activo=True)
        tenant = DummyEntity(id=50, nombre_empresa="Empresa Vencida", plan="pro_mensual", activo=True)
        past_date = datetime.now(timezone.utc) - timedelta(days=10)
        sub = DummyEntity(id=5, inquilino_id=50, plan="pro_mensual", estado="vencida", fecha_fin=past_date)

        setup_db_mock(self.db_session, tenant, sub)

        caps_dict = get_my_plan_capabilities(db=self.db_session, current_user=user)

        self.assertEqual(caps_dict["inquilino_id"], 50)
        self.assertEqual(caps_dict["canonical_plan"], "full")
        self.assertEqual(caps_dict["subscription_status"], "vencida")
        self.assertFalse(caps_dict["is_active"])
        self.assertFalse(caps_dict["crm_leads_enabled"])
        self.assertFalse(caps_dict["ai_images_enabled"])

    def test_6_tenant_isolation(self):
        """6. Aislamiento entre dos inquilinos."""
        user_a = DummyEntity(id=61, inquilino_id=601, nombre_usuario="user_a", activo=True)
        tenant_a = DummyEntity(id=601, nombre_empresa="Empresa A", plan="basico", activo=True)
        sub_a = DummyEntity(id=61, inquilino_id=601, plan="basico", estado="activa")

        user_b = DummyEntity(id=62, inquilino_id=602, nombre_usuario="user_b", activo=True)
        tenant_b = DummyEntity(id=602, nombre_empresa="Empresa B", plan="full", activo=True)
        sub_b = DummyEntity(id=62, inquilino_id=602, plan="full", estado="activa")

        setup_db_mock(self.db_session, tenant_a, sub_a)
        caps_a = get_my_plan_capabilities(db=self.db_session, current_user=user_a)

        setup_db_mock(self.db_session, tenant_b, sub_b)
        caps_b = get_my_plan_capabilities(db=self.db_session, current_user=user_b)

        self.assertEqual(caps_a["inquilino_id"], 601)
        self.assertEqual(caps_b["inquilino_id"], 602)
        self.assertFalse(caps_a["crm_leads_enabled"])
        self.assertTrue(caps_b["crm_leads_enabled"])

    def test_7_manipulated_parameter_rejection(self):
        """7. Rechazo de intentos de seleccionar otro inquilino mediante parámetros manipulados."""
        # get_my_plan_capabilities receives current_user from JWT and accepts no query params for tenant_id
        user = DummyEntity(id=7, inquilino_id=70, nombre_usuario="attacker", activo=True)
        tenant = DummyEntity(id=70, nombre_empresa="Attacker Company", plan="basico", activo=True)

        setup_db_mock(self.db_session, tenant, None)

        caps_dict = get_my_plan_capabilities(db=self.db_session, current_user=user)

        # Must resolve tenant_id 70 from JWT user, ignoring any external manipulation attempts
        self.assertEqual(caps_dict["inquilino_id"], 70)

    def test_8_response_structure_and_absence_of_secrets(self):
        """8. Estructura de respuesta y ausencia de secretos."""
        user = DummyEntity(id=8, inquilino_id=80, nombre_usuario="admin_sec", activo=True)
        tenant = DummyEntity(
            id=80,
            nombre_empresa="Secret Shield Org",
            plan="full",
            api_key="SUPER_SECRET_API_KEY_123",
            openai_api_key="sk-proj-SECRET-456",
            google_api_key="AIzaSySECRET-789",
            activo=True
        )

        setup_db_mock(self.db_session, tenant, None)

        caps_dict = get_my_plan_capabilities(db=self.db_session, current_user=user)

        # Secrets must NOT be leaked in the response dictionary
        self.assertNotIn("api_key", caps_dict)
        self.assertNotIn("openai_api_key", caps_dict)
        self.assertNotIn("google_api_key", caps_dict)
        self.assertNotIn("password_hash", caps_dict)

    def test_9_read_only_no_db_writes(self):
        """9. Ausencia de escrituras en base de datos."""
        user = DummyEntity(id=9, inquilino_id=90, nombre_usuario="read_only_user", activo=True)
        tenant = DummyEntity(id=90, nombre_empresa="Read Only Corp", plan="basico", activo=True)

        setup_db_mock(self.db_session, tenant, None)

        caps_dict = get_my_plan_capabilities(db=self.db_session, current_user=user)

        self.assertEqual(caps_dict["inquilino_id"], 90)
        # Ensure db session write/commit operations were never called
        self.db_session.add.assert_not_called()
        self.db_session.commit.assert_not_called()
        self.db_session.delete.assert_not_called()


if __name__ == "__main__":
    unittest.main()

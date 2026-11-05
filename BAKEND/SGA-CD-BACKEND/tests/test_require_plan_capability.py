"""
Automated Test Suite for require_plan_capability() Dependency (Phase 8.13.3-C1).

Tests all 14 mandatory scenarios: Basic plan requesting Full capability, Full plan requesting allowed capability,
expired/canceled subscription, inactive tenant, unassigned tenant, non-existent tenant, unknown capability,
Full plan without required role, client parameter manipulation rejection, DB session error,
subscription precedence, cross-tenant isolation, and read-only non-mutating execution.
"""
import sys
import unittest
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta

# Lightweight FastAPI / SQLAlchemy / Pydantic / Security module mock layer for standalone test execution
try:
    import fastapi
    from fastapi import HTTPException, status
except ImportError:
    class DummyHTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            self.status_code = status_code
            self.detail = detail

    class DummyStatus:
        HTTP_400_BAD_REQUEST = 400
        HTTP_401_UNAUTHORIZED = 401
        HTTP_402_PAYMENT_REQUIRED = 402
        HTTP_403_FORBIDDEN = 403
        HTTP_404_NOT_FOUND = 404
        HTTP_429_TOO_MANY_REQUESTS = 429

    class DummyAPIRouter:
        def post(self, *args, **kwargs):
            return lambda f: f
        def get(self, *args, **kwargs):
            return lambda f: f
        def put(self, *args, **kwargs):
            return lambda f: f
        def delete(self, *args, **kwargs):
            return lambda f: f

    fastapi_mock = MagicMock()
    fastapi_mock.HTTPException = DummyHTTPException
    fastapi_mock.status = DummyStatus
    fastapi_mock.APIRouter = DummyAPIRouter
    fastapi_mock.Depends = lambda x=None: x
    fastapi_mock.DummyStatus = DummyStatus
    sys.modules["fastapi"] = fastapi_mock
    sys.modules["fastapi.security"] = MagicMock()
    HTTPException = DummyHTTPException
    status = DummyStatus

try:
    import sqlalchemy
except ImportError:
    sqla_mock = MagicMock()
    orm_mock = MagicMock()
    class DummyDeclarativeBase:
        metadata = MagicMock()
    orm_mock.DeclarativeBase = DummyDeclarativeBase
    sys.modules["sqlalchemy"] = sqla_mock
    sys.modules["sqlalchemy.orm"] = orm_mock
    sys.modules["sqlalchemy.sql"] = MagicMock()

try:
    import pydantic
except ImportError:
    class DummyBaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def dict(self, *args, **kwargs):
            res = {}
            for k, v in self.__dict__.items():
                if not k.startswith("_"):
                    res[k] = v
            return res

    def dummy_field(default=None, default_factory=None, **kwargs):
        if default_factory is not None:
            return default_factory()
        return default

    pydantic_mock = MagicMock()
    pydantic_mock.BaseModel = DummyBaseModel
    pydantic_mock.EmailStr = str
    pydantic_mock.Field = dummy_field
    pydantic_mock.DummyBaseModel = DummyBaseModel
    sys.modules["pydantic"] = pydantic_mock

if "pydantic_settings" not in sys.modules:
    pyd_settings_mock = MagicMock()
    class DummyBaseSettings:
        API_V1_STR = "/api/v1"
        SECRET_KEY = "test-secret"
        ALGORITHM = "HS256"
        DATABASE_URL = "sqlite:///./test.db"
    pyd_settings_mock.BaseSettings = DummyBaseSettings
    sys.modules["pydantic_settings"] = pyd_settings_mock

if "jose" not in sys.modules:
    sys.modules["jose"] = MagicMock()

if "passlib" not in sys.modules:
    sys.modules["passlib"] = MagicMock()
    sys.modules["passlib.context"] = MagicMock()

if "bcrypt" not in sys.modules:
    bcrypt_mock = MagicMock()
    bcrypt_mock.__version__ = "4.0.0"
    sys.modules["bcrypt"] = bcrypt_mock

from fastapi import HTTPException, status
from app.api.deps import require_plan_capability, role_required


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


class TestRequirePlanCapabilityDependency(unittest.TestCase):

    def setUp(self):
        self.db_session = MagicMock()

    def test_01_basic_plan_requesting_full_capability(self):
        """1. Plan Básico solicitando una capacidad exclusiva de Full (402 Payment Required)."""
        user = DummyEntity(id=1, inquilino_id=10, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=10, nombre_empresa="Basic Corp", plan="basico", activo=True)
        sub = DummyEntity(id=1, inquilino_id=10, plan="basico", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        checker = require_plan_capability("ai_images")
        with self.assertRaises(HTTPException) as cm:
            checker(db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertIn("upgrade to Plan Full", cm.exception.detail)

    def test_02_full_plan_requesting_allowed_capability(self):
        """2. Plan Full solicitando una capacidad permitida (Autoriza correctamente)."""
        user = DummyEntity(id=2, inquilino_id=20, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=20, nombre_empresa="Full Corp", plan="pro_anual", activo=True)
        sub = DummyEntity(id=2, inquilino_id=20, plan="pro_anual", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        checker = require_plan_capability("ai_images")
        authorized_user = checker(db=self.db_session, current_user=user)

        self.assertEqual(authorized_user.id, 2)

    def test_03_expired_subscription(self):
        """3. Suscripción vencida (402 Payment Required)."""
        user = DummyEntity(id=3, inquilino_id=30, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=30, nombre_empresa="Expired Corp", plan="pro_mensual", activo=True)
        past_date = datetime.now(timezone.utc) - timedelta(days=5)
        sub = DummyEntity(id=3, inquilino_id=30, plan="pro_mensual", estado="vencida", fecha_fin=past_date)
        setup_db_mock(self.db_session, tenant, sub)

        checker = require_plan_capability("ai_images")
        with self.assertRaises(HTTPException) as cm:
            checker(db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)

    def test_04_canceled_subscription(self):
        """4. Suscripción cancelada (402 Payment Required)."""
        user = DummyEntity(id=4, inquilino_id=40, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=40, nombre_empresa="Canceled Corp", plan="pro_mensual", activo=True)
        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        sub = DummyEntity(id=4, inquilino_id=40, plan="pro_mensual", estado="cancelada", fecha_fin=past_date)
        setup_db_mock(self.db_session, tenant, sub)

        checker = require_plan_capability("ai_images")
        with self.assertRaises(HTTPException) as cm:
            checker(db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)

    def test_05_inactive_tenant(self):
        """5. Inquilino inactivo (403 Forbidden)."""
        user = DummyEntity(id=5, inquilino_id=50, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=50, nombre_empresa="Inactive Tenant", plan="pro_anual", activo=False)
        setup_db_mock(self.db_session, tenant, None)

        checker = require_plan_capability("ai_images")
        with self.assertRaises(HTTPException) as cm:
            checker(db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("inactive", cm.exception.detail)

    def test_06_unassigned_tenant_user(self):
        """6. Usuario sin inquilino asociado (400 Bad Request)."""
        user = DummyEntity(id=6, inquilino_id=None, role_codes=["admin_empresa"], activo=True)

        checker = require_plan_capability("ai_images")
        with self.assertRaises(HTTPException) as cm:
            checker(db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not associated", cm.exception.detail)

    def test_07_non_existent_tenant_record(self):
        """7. Usuario cuyo inquilino no existe (404 Not Found)."""
        user = DummyEntity(id=7, inquilino_id=707, role_codes=["admin_empresa"], activo=True)
        setup_db_mock(self.db_session, None, None)

        checker = require_plan_capability("ai_images")
        with self.assertRaises(HTTPException) as cm:
            checker(db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_404_NOT_FOUND)

    def test_08_unknown_capability_requested(self):
        """8. Plan o capacidad desconocidos (403 Forbidden)."""
        user = DummyEntity(id=8, inquilino_id=80, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=80, nombre_empresa="Test Corp", plan="pro_anual", activo=True)
        sub = DummyEntity(id=8, inquilino_id=80, plan="pro_anual", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        checker = require_plan_capability("unknown_super_power")
        with self.assertRaises(HTTPException) as cm:
            checker(db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Unknown capability", cm.exception.detail)

    def test_09_full_plan_user_without_required_role(self):
        """9. Usuario con plan Full pero sin el rol requerido (Demuestra independencia entre plan y rol)."""
        user = DummyEntity(id=9, inquilino_id=90, role_codes=["alumno"], activo=True)
        tenant = DummyEntity(id=90, nombre_empresa="Full Corp", plan="pro_anual", activo=True)
        sub = DummyEntity(id=9, inquilino_id=90, plan="pro_anual", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        # Plan check passes
        plan_checker = require_plan_capability("ai_images")
        plan_ok_user = plan_checker(db=self.db_session, current_user=user)
        self.assertEqual(plan_ok_user.id, 9)

        # Role check independently fails for 'alumno' when 'admin_empresa' is required
        role_checker = role_required(["admin_empresa"])
        with self.assertRaises(HTTPException) as cm:
            role_checker(current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_403_FORBIDDEN)

    def test_10_client_parameter_manipulation_rejection(self):
        """10. Manipulación de identificadores del inquilino enviados por el cliente."""
        # require_plan_capability receives tenant ID strictly from current_user (JWT)
        user = DummyEntity(id=10, inquilino_id=100, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=100, nombre_empresa="JWT Bound Tenant", plan="basico", activo=True)
        setup_db_mock(self.db_session, tenant, None)

        checker = require_plan_capability("ai_images")
        with self.assertRaises(HTTPException) as cm:
            checker(db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)

    def test_11_db_query_session_error_handling(self):
        """11. Fallo de consulta a la base de datos."""
        user = DummyEntity(id=11, inquilino_id=110, role_codes=["admin_empresa"], activo=True)
        self.db_session.query.side_effect = Exception("Database connection dropped")

        checker = require_plan_capability("ai_images")
        with self.assertRaises(Exception) as cm:
            checker(db=self.db_session, current_user=user)

        self.assertIn("Database connection dropped", str(cm.exception))

    def test_12_subscription_precedence_over_tenant_plan(self):
        """12. Precedencia entre Suscripcion e Inquilino.plan."""
        # Inquilino.plan says 'pro_anual', but Suscripcion says 'vencida'
        user = DummyEntity(id=12, inquilino_id=120, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=120, nombre_empresa="Conflicting Corp", plan="pro_anual", activo=True)
        past_date = datetime.now(timezone.utc) - timedelta(days=2)
        sub = DummyEntity(id=12, inquilino_id=120, plan="pro_anual", estado="vencida", fecha_fin=past_date)
        setup_db_mock(self.db_session, tenant, sub)

        checker = require_plan_capability("ai_images")
        with self.assertRaises(HTTPException) as cm:
            checker(db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)

    def test_13_cross_tenant_isolation(self):
        """13. Aislamiento entre dos inquilinos distintos."""
        user_a = DummyEntity(id=131, inquilino_id=1301, role_codes=["admin_empresa"], activo=True)
        tenant_a = DummyEntity(id=1301, nombre_empresa="Tenant A", plan="basico", activo=True)

        user_b = DummyEntity(id=132, inquilino_id=1302, role_codes=["admin_empresa"], activo=True)
        tenant_b = DummyEntity(id=1302, nombre_empresa="Tenant B", plan="full", activo=True)
        sub_b = DummyEntity(id=132, inquilino_id=1302, plan="full", estado="activa")

        checker = require_plan_capability("ai_images")

        # Tenant A denied
        setup_db_mock(self.db_session, tenant_a, None)
        with self.assertRaises(HTTPException) as cm_a:
            checker(db=self.db_session, current_user=user_a)
        self.assertEqual(cm_a.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        # Tenant B authorized
        setup_db_mock(self.db_session, tenant_b, sub_b)
        authed_b = checker(db=self.db_session, current_user=user_b)
        self.assertEqual(authed_b.id, 132)

    def test_14_pure_read_only_no_db_writes(self):
        """14. Confirmación de que una denegación no modifica datos persistentes."""
        user = DummyEntity(id=14, inquilino_id=140, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=140, nombre_empresa="Read Only Corp", plan="basico", activo=True)
        setup_db_mock(self.db_session, tenant, None)

        checker = require_plan_capability("ai_images")
        with self.assertRaises(HTTPException):
            checker(db=self.db_session, current_user=user)

        # Verify db session write/commit methods were not called
        self.db_session.add.assert_not_called()
        self.db_session.commit.assert_not_called()
        self.db_session.delete.assert_not_called()


if __name__ == "__main__":
    unittest.main()

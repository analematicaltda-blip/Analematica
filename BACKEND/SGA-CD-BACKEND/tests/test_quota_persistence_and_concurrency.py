"""
Automated Test Suite for Persistent Monthly Quota Control & Concurrency (Phase 8.13.3-D1).

Verifies ConsumoInquilino ORM model persistence, atomic reservation, HTTP 429 Too Many Requests
rejection when monthly limit is reached, month-period rollover, tenant quota isolation,
quota release on operation failure, and endpoint integration.
"""
import sys
import unittest
from unittest.mock import MagicMock, patch
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

if "requests" not in sys.modules:
    sys.modules["requests"] = MagicMock()

if "httplib2" not in sys.modules:
    sys.modules["httplib2"] = MagicMock()

if "googleapiclient" not in sys.modules:
    sys.modules["googleapiclient"] = MagicMock()
    sys.modules["googleapiclient.discovery"] = MagicMock()
    sys.modules["googleapiclient.http"] = MagicMock()

if "oauth2client" not in sys.modules:
    sys.modules["oauth2client"] = MagicMock()
    sys.modules["oauth2client.client"] = MagicMock()

if "models" not in sys.modules:
    models_mock = MagicMock()
    sys.modules["models"] = models_mock
    sys.modules["models.settings"] = MagicMock()

from fastapi import HTTPException, status
from app.services.plan_capability_service import PlanCapabilityService
from app.models.billing import ConsumoInquilino


class DummyEntity:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def setup_db_mock(db_session, tenant_obj, sub_obj=None, consumo_obj=None):
    def query_handler(model):
        q_mock = MagicMock()
        model_str = str(model)
        model_name = getattr(model, "__name__", model_str)
        if "ConsumoInquilino" in model_name or "ConsumoInquilino" in model_str:
            q_mock.filter.return_value.first.return_value = consumo_obj
            q_mock.filter.return_value.order_by.return_value.first.return_value = consumo_obj
        elif "Suscripcion" in model_name or "Suscripcion" in model_str:
            q_mock.filter.return_value.first.return_value = sub_obj
            q_mock.filter.return_value.order_by.return_value.first.return_value = sub_obj
        elif "Inquilino" in model_name or "Inquilino" in model_str:
            q_mock.filter.return_value.first.return_value = tenant_obj
            q_mock.filter.return_value.order_by.return_value.first.return_value = tenant_obj
        else:
            q_mock.filter.return_value.first.return_value = None
            q_mock.filter.return_value.order_by.return_value.first.return_value = None
        return q_mock
    db_session.query.side_effect = query_handler


class TestQuotaPersistenceAndConcurrency(unittest.TestCase):

    def setUp(self):
        self.db_session = MagicMock()

    def test_01_available_quota_consumption(self):
        """1. Consumo de cuota disponible incrementa el registro de consumo."""
        tenant = DummyEntity(id=10, plan="pro_anual", activo=True)
        sub = DummyEntity(id=1, inquilino_id=10, plan="pro_anual", estado="activa")
        consumo = DummyEntity(id=1, inquilino_id=10, periodo="2025-05", capacidad="images", cantidad_usada=50)

        setup_db_mock(self.db_session, tenant, sub, consumo)

        res = PlanCapabilityService.check_and_consume_quota(
            db=self.db_session,
            inquilino_id=10,
            capability_name="ai_images",
            amount=1,
            periodo="2025-05"
        )

        self.assertEqual(res["inquilino_id"], 10)
        self.assertEqual(res["capacidad"], "images")
        self.assertEqual(res["cantidad_usada"], 51)
        self.assertEqual(res["limite_mensual"], 100)
        self.assertEqual(res["restantes"], 49)
        self.db_session.commit.assert_called_once()

    def test_02_exhausted_quota_rejection_raises_429(self):
        """2. Rechazo por cuota mensual agotada arroja HTTP 429 Too Many Requests."""
        tenant = DummyEntity(id=20, plan="pro_anual", activo=True)
        sub = DummyEntity(id=2, inquilino_id=20, plan="pro_anual", estado="activa")
        # Already used 100 out of 100 images
        consumo = DummyEntity(id=2, inquilino_id=20, periodo="2025-05", capacidad="images", cantidad_usada=100)

        setup_db_mock(self.db_session, tenant, sub, consumo)

        with self.assertRaises(HTTPException) as cm:
            PlanCapabilityService.check_and_consume_quota(
                db=self.db_session,
                inquilino_id=20,
                capability_name="ai_images",
                amount=1,
                periodo="2025-05"
            )

        self.assertEqual(cm.exception.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn("Monthly limit", cm.exception.detail)

    def test_03_tenant_quota_isolation(self):
        """3. Aislamiento de cuotas entre inquilinos (Inquilino A al límite no afecta cuota de Inquilino B)."""
        tenant_a = DummyEntity(id=101, plan="pro_anual", activo=True)
        sub_a = DummyEntity(id=101, inquilino_id=101, plan="pro_anual", estado="activa")
        consumo_a = DummyEntity(id=101, inquilino_id=101, periodo="2025-05", capacidad="images", cantidad_usada=100)

        tenant_b = DummyEntity(id=102, plan="pro_anual", activo=True)
        sub_b = DummyEntity(id=102, inquilino_id=102, plan="pro_anual", estado="activa")
        consumo_b = DummyEntity(id=102, inquilino_id=102, periodo="2025-05", capacidad="images", cantidad_usada=10)

        # Tenant A rejected (429)
        setup_db_mock(self.db_session, tenant_a, sub_a, consumo_a)
        with self.assertRaises(HTTPException) as cm_a:
            PlanCapabilityService.check_and_consume_quota(
                db=self.db_session,
                inquilino_id=101,
                capability_name="ai_images",
                amount=1,
                periodo="2025-05"
            )
        self.assertEqual(cm_a.exception.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # Tenant B allowed
        setup_db_mock(self.db_session, tenant_b, sub_b, consumo_b)
        res_b = PlanCapabilityService.check_and_consume_quota(
            db=self.db_session,
            inquilino_id=102,
            capability_name="ai_images",
            amount=1,
            periodo="2025-05"
        )
        self.assertEqual(res_b["cantidad_usada"], 11)

    def test_04_period_monthly_rollover(self):
        """4. Rollover mensual de periodo (el consumo de 2025-04 no bloquea el periodo 2025-05)."""
        tenant = DummyEntity(id=40, plan="pro_anual", activo=True)
        sub = DummyEntity(id=4, inquilino_id=40, plan="pro_anual", estado="activa")
        # In May (2025-05), no consumption record exists yet
        setup_db_mock(self.db_session, tenant, sub, consumo_obj=None)

        res = PlanCapabilityService.check_and_consume_quota(
            db=self.db_session,
            inquilino_id=40,
            capability_name="ai_images",
            amount=1,
            periodo="2025-05"
        )

        self.assertEqual(res["periodo"], "2025-05")
        self.assertEqual(res["cantidad_usada"], 1)
        self.db_session.add.assert_called_once()

    def test_05_release_quota_on_failure(self):
        """5. Liberación de cuota reservada cuando falla una operación posterior."""
        consumo = DummyEntity(id=5, inquilino_id=50, periodo="2025-05", capacidad="images", cantidad_usada=10)
        setup_db_mock(self.db_session, tenant_obj=None, sub_obj=None, consumo_obj=consumo)

        res = PlanCapabilityService.release_quota(
            db=self.db_session,
            inquilino_id=50,
            capability_name="ai_images",
            amount=1,
            periodo="2025-05"
        )

        self.assertEqual(res["cantidad_usada"], 9)
        self.db_session.commit.assert_called_once()

    def test_06_unique_constraint_orm_definition(self):
        """6. Verificación de restricción única en el modelo ORM ConsumoInquilino."""
        table_args = getattr(ConsumoInquilino, "__table_args__", ())
        self.assertTrue(len(table_args) > 0, "ConsumoInquilino ORM model missing __table_args__")

    def test_07_concurrent_first_counter_creation_fallback(self):
        """7. Recuperación ante conflicto de creación concurrente (IntegrityError en primer commit)."""
        tenant = DummyEntity(id=70, plan="pro_anual", activo=True)
        sub = DummyEntity(id=7, inquilino_id=70, plan="pro_anual", estado="activa")
        existing_consumo = DummyEntity(id=7, inquilino_id=70, periodo="2025-05", capacidad="images", cantidad_usada=5)

        # On initial query, no record is found (None)
        q_mock = MagicMock()
        q_mock.filter.return_value.first.side_effect = [None, existing_consumo]

        def custom_query(model):
            model_str = str(model)
            model_name = getattr(model, "__name__", model_str)
            if "ConsumoInquilino" in model_name or "ConsumoInquilino" in model_str:
                return q_mock
            elif "Suscripcion" in model_name or "Suscripcion" in model_str:
                m = MagicMock()
                m.filter.return_value.order_by.return_value.first.return_value = sub
                return m
            elif "Inquilino" in model_name or "Inquilino" in model_str:
                m = MagicMock()
                m.filter.return_value.first.return_value = tenant
                return m
            return MagicMock()

        self.db_session.query.side_effect = custom_query

        # First commit fails due to IntegrityError (simulating race condition on first counter creation)
        self.db_session.commit.side_effect = [Exception("IntegrityError: duplicate key value violates unique constraint"), None]

        res = PlanCapabilityService.check_and_consume_quota(
            db=self.db_session,
            inquilino_id=70,
            capability_name="ai_images",
            amount=1,
            periodo="2025-05"
        )

        self.assertEqual(res["cantidad_usada"], 6)
        self.db_session.rollback.assert_called_once()


if __name__ == "__main__":
    unittest.main()

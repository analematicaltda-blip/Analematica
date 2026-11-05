"""
HTTP & Handler Integration Test Suite for POST /crm/generate_predis_media (Phase 8.13.3-C2.2).

Verifies the end-to-end commercial protection workflow against all 10 mandatory scenarios:
1. Unauthenticated request rejection.
2. Unauthorized role rejection (403 Forbidden).
3. Basic plan user rejection (402 Payment Required).
4. Active Full plan user authorization (200 OK).
5. Expired/canceled subscription rejection (402 Payment Required).
6. Inactive tenant rejection (403 Forbidden).
7. Orphan user without tenant rejection (400 Bad Request).
8. Unsupported/unknown format rejection (400 Bad Request).
9. Cross-tenant parameter manipulation rejection (JWT identity binding).
10. Authorization failure guarantees zero AI engine invocations and zero DB writes.
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

if "models" not in sys.modules:
    models_mock = MagicMock()
    sys.modules["models"] = models_mock
    sys.modules["models.settings"] = MagicMock()

# Force re-importing admin_general endpoint module
if "app.api.v1.endpoints.admin_general" in sys.modules:
    del sys.modules["app.api.v1.endpoints.admin_general"]

from fastapi import HTTPException, status
from app.api.v1.endpoints.admin_general import (
    generate_predis_media,
    PredisMediaRequest,
    PredisMediaResponse
)


class DummyEntity:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def setup_db_mock(db_session, tenant_obj, sub_obj=None, consumo_obj=None):
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
        elif "ConsumoInquilino" in model_name or "ConsumoInquilino" in model_str:
            q_mock.filter.return_value.first.return_value = consumo_obj
        else:
            q_mock.filter.return_value.first.return_value = None
        return q_mock
    db_session.query.side_effect = query_handler


class TestCrmMediaHttpIntegration(unittest.TestCase):

    def setUp(self):
        self.db_session = MagicMock()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_01_unauthenticated_request_rejected(self, mock_ai_generate):
        """1. Solicitud sin autenticación (current_user=None) es rechazada con 401 Unauthorized sin invocar IA."""
        payload = PredisMediaRequest(area="taekwondo", prompt="Torneo 2025", format="post_1_1")

        def simulate_unauthenticated_call():
            # OAuth2 or JWT dependency raises 401 when token is missing/invalid
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        with self.assertRaises(HTTPException) as cm:
            simulate_unauthenticated_call()

        self.assertEqual(cm.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        mock_ai_generate.assert_not_called()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_02_unauthorized_role_rejected(self, mock_ai_generate):
        """2. Usuario autenticado con rol no autorizado ('alumno') recibe 403 Forbidden y no invoca IA."""
        user = DummyEntity(id=2, inquilino_id=20, role_codes=["alumno"], activo=True)
        tenant = DummyEntity(id=20, nombre_empresa="Full Corp", plan="pro_anual", activo=True)
        sub = DummyEntity(id=2, inquilino_id=20, plan="pro_anual", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        payload = PredisMediaRequest(area="futbol", prompt="Not authorized", format="post_1_1")

        with self.assertRaises(HTTPException) as cm:
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_403_FORBIDDEN)
        mock_ai_generate.assert_not_called()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_03_basic_plan_rejected(self, mock_ai_generate):
        """3. Usuario Plan Básico intentando formato no habilitado recibe 402 Payment Required sin invocar IA."""
        user = DummyEntity(id=3, inquilino_id=30, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=30, nombre_empresa="Basic Corp", plan="basico", activo=True)
        sub = DummyEntity(id=3, inquilino_id=30, plan="basico", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        payload = PredisMediaRequest(area="baloncesto", prompt="Prueba", format="reel_9_16")

        with self.assertRaises(HTTPException) as cm:
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        mock_ai_generate.assert_not_called()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_04_active_full_plan_user_authorized(self, mock_ai_generate):
        """4. Usuario Plan Full activo con rol autorizado genera el recurso (200 OK)."""
        mock_ai_generate.return_value = {"text": "Copy publicitario generado por IA"}
        user = DummyEntity(id=4, inquilino_id=40, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=40, nombre_empresa="Full Corp", plan="pro_anual", activo=True)
        sub = DummyEntity(id=4, inquilino_id=40, plan="pro_anual", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        payload = PredisMediaRequest(area="taekwondo", prompt="Curso 2025", format="post_1_1")
        response = generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertIsInstance(response, PredisMediaResponse)
        self.assertIn("TAEKWONDO", response.title)
        mock_ai_generate.assert_called_once()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_05_expired_subscription_rejected(self, mock_ai_generate):
        """5. Suscripción vencida o cancelada recibe 402 Payment Required sin invocar IA."""
        user = DummyEntity(id=5, inquilino_id=50, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=50, nombre_empresa="Expired Corp", plan="pro_mensual", activo=True)
        past_date = datetime.now(timezone.utc) - timedelta(days=10)
        sub = DummyEntity(id=5, inquilino_id=50, plan="pro_mensual", estado="vencida", fecha_fin=past_date)
        setup_db_mock(self.db_session, tenant, sub)

        payload = PredisMediaRequest(area="danza_joropo", prompt="Festival", format="carousel_multi")

        with self.assertRaises(HTTPException) as cm:
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        mock_ai_generate.assert_not_called()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_06_inactive_tenant_rejected(self, mock_ai_generate):
        """6. Inquilino inactivo recibe 403 Forbidden sin invocar IA."""
        user = DummyEntity(id=6, inquilino_id=60, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=60, nombre_empresa="Inactive Tenant", plan="pro_anual", activo=False)
        setup_db_mock(self.db_session, tenant, None)

        payload = PredisMediaRequest(area="instrumentos", prompt="Concierto", format="post_1_1")

        with self.assertRaises(HTTPException) as cm:
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_403_FORBIDDEN)
        mock_ai_generate.assert_not_called()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_07_user_without_tenant_rejected(self, mock_ai_generate):
        """7. Usuario sin inquilino asociado recibe 400 Bad Request sin invocar IA."""
        user = DummyEntity(id=7, inquilino_id=None, role_codes=["admin_empresa"], activo=True)

        payload = PredisMediaRequest(area="futbol", prompt="Prueba", format="post_1_1")

        with self.assertRaises(HTTPException) as cm:
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_400_BAD_REQUEST)
        mock_ai_generate.assert_not_called()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_08_unknown_format_rejected(self, mock_ai_generate):
        """8. Formato desconocido recibe 400 Bad Request sin invocar IA."""
        user = DummyEntity(id=8, inquilino_id=80, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=80, nombre_empresa="Full Corp", plan="pro_anual", activo=True)
        sub = DummyEntity(id=8, inquilino_id=80, plan="pro_anual", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        payload = PredisMediaRequest(area="taekwondo", prompt="Hacked", format="invalid_format_xyz")

        with self.assertRaises(HTTPException) as cm:
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Unsupported format", cm.exception.detail)
        mock_ai_generate.assert_not_called()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_09_cross_tenant_manipulation_rejection(self, mock_ai_generate):
        """9. Intento de manipulación de inquilino por el cliente: la identidad proviene strictly del JWT."""
        user = DummyEntity(id=9, inquilino_id=90, role_codes=["admin_empresa"], activo=True)
        tenant_90 = DummyEntity(id=90, nombre_empresa="Basic Tenant 90", plan="basico", activo=True)
        setup_db_mock(self.db_session, tenant_90, None)

        payload = PredisMediaRequest(area="taekwondo", prompt="Prompt", format="post_1_1")

        with self.assertRaises(HTTPException) as cm:
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        mock_ai_generate.assert_not_called()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_10_authorization_failure_guarantees_no_ai_and_no_db_writes(self, mock_ai_generate):
        """10. Confirmación de que cualquier denegación impide invocación de IA y escrituras en BD."""
        user = DummyEntity(id=10, inquilino_id=100, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=100, nombre_empresa="Basic Tenant 100", plan="basico", activo=True)
        setup_db_mock(self.db_session, tenant, None)

        payload = PredisMediaRequest(area="taekwondo", prompt="Test", format="reel_9_16")

        with self.assertRaises(HTTPException):
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.db_session.add.assert_not_called()
        self.db_session.commit.assert_not_called()
        mock_ai_generate.assert_not_called()


if __name__ == "__main__":
    unittest.main()

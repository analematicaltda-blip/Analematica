"""
Automated Endpoint Protection Test Suite for POST /crm/generate_predis_media (Phase 8.13.3-C2).

Verifies commercial capability gate integration on CRM media generation endpoint,
ensuring Basic plan users, expired subscriptions, inactive tenants, and unauthorized roles
are rejected BEFORE initiating AI router inference or rendering pipelines.
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
    pass

try:
    import pydantic_settings
except ImportError:
    pyd_settings_mock = MagicMock()
    class DummyBaseSettings:
        API_V1_STR = "/api/v1"
        SECRET_KEY = "test-secret"
        ALGORITHM = "HS256"
        DATABASE_URL = "sqlite:///./test.db"
    pyd_settings_mock.BaseSettings = DummyBaseSettings
    sys.modules["pydantic_settings"] = pyd_settings_mock

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


class TestCrmMediaCapabilityProtection(unittest.TestCase):

    def setUp(self):
        self.db_session = MagicMock()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_01_full_plan_user_authorized_post_image(self, mock_ai_generate):
        """1. Usuario Plan Full autorizado solicitando formato post_1_1 (AI Images)."""
        mock_ai_generate.return_value = {"text": "Copy publicitario optimizado por IA"}
        user = DummyEntity(id=1, inquilino_id=10, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=10, nombre_empresa="Full Corp", plan="pro_anual", activo=True)
        sub = DummyEntity(id=1, inquilino_id=10, plan="pro_anual", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        payload = PredisMediaRequest(area="taekwondo", prompt="Torneo 2025", format="post_1_1")
        response = generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertIsInstance(response, PredisMediaResponse)
        self.assertIn("TAEKWONDO", response.title)
        self.assertIn("1080x1080", response.dimensions)
        mock_ai_generate.assert_called_once()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_02_full_plan_user_authorized_carousel(self, mock_ai_generate):
        """2. Usuario Plan Full autorizado solicitando formato carousel_multi (AI Carousels)."""
        mock_ai_generate.return_value = {"text": "Copy carrusel IA"}
        user = DummyEntity(id=2, inquilino_id=20, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=20, nombre_empresa="Full Corp B", plan="pro_anual", activo=True)
        sub = DummyEntity(id=2, inquilino_id=20, plan="pro_anual", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        payload = PredisMediaRequest(area="futbol", prompt="Escuela infantil", format="carousel_multi")
        response = generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertEqual(response.status, "rendered")
        self.assertIn("1080x1350", response.dimensions)

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_03_full_plan_user_authorized_reel(self, mock_ai_generate):
        """3. Usuario Plan Full autorizado solicitando formato reel_9_16 (AI Reels)."""
        mock_ai_generate.return_value = {"text": "Copy reel IA"}
        user = DummyEntity(id=3, inquilino_id=30, role_codes=["admin_general"], activo=True)
        tenant = DummyEntity(id=30, nombre_empresa="Root Corp", plan="full", activo=True)
        sub = DummyEntity(id=3, inquilino_id=30, plan="full", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        payload = PredisMediaRequest(area="danza_joropo", prompt="Festival", format="reel_9_16")
        response = generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertIn("1080x1920", response.dimensions)

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_04_basic_plan_denied_image_generation(self, mock_ai_generate):
        """4. Usuario Plan Básico intentando generación de imagen (402 Payment Required BEFORE AI router)."""
        user = DummyEntity(id=4, inquilino_id=40, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=40, nombre_empresa="Basic Corp", plan="basico", activo=True)
        sub = DummyEntity(id=4, inquilino_id=40, plan="basico", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        payload = PredisMediaRequest(area="baloncesto", prompt="Inscripciones", format="post_1_1")

        with self.assertRaises(HTTPException) as cm:
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        mock_ai_generate.assert_not_called()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_05_basic_plan_denied_reel_generation(self, mock_ai_generate):
        """5. Usuario Plan Básico intentando generación de reel (402 Payment Required)."""
        user = DummyEntity(id=5, inquilino_id=50, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=50, nombre_empresa="Basic Corp 2", plan="basico", activo=True)
        setup_db_mock(self.db_session, tenant, None)

        payload = PredisMediaRequest(area="instrumentos", prompt="Concierto", format="reel_9_16")

        with self.assertRaises(HTTPException) as cm:
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        mock_ai_generate.assert_not_called()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_06_expired_subscription_denied(self, mock_ai_generate):
        """6. Suscripción vencida intentando generación (402 Payment Required)."""
        user = DummyEntity(id=6, inquilino_id=60, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=60, nombre_empresa="Expired Corp", plan="pro_anual", activo=True)
        past_date = datetime.now(timezone.utc) - timedelta(days=10)
        sub = DummyEntity(id=6, inquilino_id=60, plan="pro_anual", estado="vencida", fecha_fin=past_date)
        setup_db_mock(self.db_session, tenant, sub)

        payload = PredisMediaRequest(area="taekwondo", prompt="Curso", format="post_1_1")

        with self.assertRaises(HTTPException) as cm:
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        mock_ai_generate.assert_not_called()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_07_inactive_tenant_denied(self, mock_ai_generate):
        """7. Inquilino inactivo intentando generación (403 Forbidden)."""
        user = DummyEntity(id=7, inquilino_id=70, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=70, nombre_empresa="Inactive Tenant", plan="pro_anual", activo=False)
        setup_db_mock(self.db_session, tenant, None)

        payload = PredisMediaRequest(area="futbol", prompt="Torneo", format="post_1_1")

        with self.assertRaises(HTTPException) as cm:
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_403_FORBIDDEN)
        mock_ai_generate.assert_not_called()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_08_orphan_user_without_tenant_denied(self, mock_ai_generate):
        """8. Usuario sin inquilino asociado (400 Bad Request)."""
        user = DummyEntity(id=8, inquilino_id=None, role_codes=["admin_empresa"], activo=True)

        payload = PredisMediaRequest(area="futbol", prompt="Torneo", format="post_1_1")

        with self.assertRaises(HTTPException) as cm:
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_400_BAD_REQUEST)
        mock_ai_generate.assert_not_called()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_09_full_plan_user_unauthorized_role_denied(self, mock_ai_generate):
        """9. Usuario con plan Full pero rol no autorizado (ej. alumno) es rechazado con 403 por el control de rol."""
        user = DummyEntity(id=9, inquilino_id=90, role_codes=["alumno"], activo=True)
        tenant = DummyEntity(id=90, nombre_empresa="Full Corp", plan="pro_anual", activo=True)
        sub = DummyEntity(id=9, inquilino_id=90, plan="pro_anual", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        payload = PredisMediaRequest(area="taekwondo", prompt="Curso", format="post_1_1")

        with self.assertRaises(HTTPException) as cm:
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_403_FORBIDDEN)
        mock_ai_generate.assert_not_called()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_10_read_only_no_db_writes_on_denial(self, mock_ai_generate):
        """10. Confirmación de que las denegaciones no invocan escrituras en BD ni servicios de IA."""
        user = DummyEntity(id=10, inquilino_id=100, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=100, nombre_empresa="Basic Corp 3", plan="basico", activo=True)
        setup_db_mock(self.db_session, tenant, None)

        payload = PredisMediaRequest(area="taekwondo", prompt="Promoción", format="reel_9_16")

        with self.assertRaises(HTTPException):
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.db_session.add.assert_not_called()
        self.db_session.commit.assert_not_called()
        mock_ai_generate.assert_not_called()

    @patch("app.api.v1.endpoints.admin_general.ai_router.generate_text")
    def test_11_unsupported_format_rejected_with_400(self, mock_ai_generate):
        """11. Formato no soportado o desconocido es rechazado con HTTP 400 Bad Request."""
        user = DummyEntity(id=11, inquilino_id=110, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=110, nombre_empresa="Full Corp", plan="pro_anual", activo=True)
        sub = DummyEntity(id=11, inquilino_id=110, plan="pro_anual", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        payload = PredisMediaRequest(area="taekwondo", prompt="Hacked Prompt", format="unsupported_format_xyz")

        with self.assertRaises(HTTPException) as cm:
            generate_predis_media(payload=payload, db=self.db_session, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Unsupported format", cm.exception.detail)
        mock_ai_generate.assert_not_called()


if __name__ == "__main__":
    unittest.main()

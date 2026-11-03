"""
Automated Endpoint Protection Test Suite for POST /video_distribution/publish (Phase 8.13.3-C3).

Verifies commercial capability gate integration on social video distribution endpoint,
ensuring Basic plan users, expired subscriptions, inactive tenants, and unauthorized roles
are rejected BEFORE initiating social media API upload calls or video downloading tasks.
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

    class DummyAPIRouter:
        def post(self, *args, **kwargs):
            return lambda f: f
        def get(self, *args, **kwargs):
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

# Force re-importing video_distribution endpoint module
if "app.api.v1.endpoints.video_distribution" in sys.modules:
    del sys.modules["app.api.v1.endpoints.video_distribution"]

from fastapi import HTTPException, status
from app.api.v1.endpoints.video_distribution import (
    publish_video,
    DistributionRequest
)


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


class TestVideoDistributionCapabilityProtection(unittest.TestCase):

    def setUp(self):
        self.db_session = MagicMock()
        self.dist_service = MagicMock()

    def test_01_basic_plan_denied_social_publishing(self):
        """1. Usuario Plan Básico intentando publicación social (402 Payment Required BEFORE distribution service)."""
        user = DummyEntity(id=1, inquilino_id=10, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=10, nombre_empresa="Basic Corp", plan="basico", activo=True)
        sub = DummyEntity(id=1, inquilino_id=10, plan="basico", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        req = DistributionRequest(
            platforms=["youtube", "instagram"],
            video_url="https://sga-cd.org/video.mp4",
            title="Promo 2025",
            description="Lanzamiento"
        )

        with self.assertRaises(HTTPException) as cm:
            publish_video(
                request_in=req,
                db=self.db_session,
                distribution_service=self.dist_service,
                current_user=user
            )

        self.assertEqual(cm.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.dist_service.publish_video.assert_not_called()

    def test_02_full_plan_user_authorized_social_publishing(self):
        """2. Usuario Plan Full activo con rol autorizado publica exitosamente (200 OK)."""
        self.dist_service.publish_video.return_value = {"status": "success", "platform": "youtube", "post_url": "https://youtube.com/watch?v=123"}
        user = DummyEntity(id=2, inquilino_id=20, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=20, nombre_empresa="Full Corp", plan="pro_anual", activo=True)
        sub = DummyEntity(id=2, inquilino_id=20, plan="pro_anual", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        req = DistributionRequest(
            platforms=["youtube"],
            video_url="https://sga-cd.org/video.mp4",
            title="Promo Full 2025",
            description="Lanzamiento Institucional"
        )

        res = publish_video(
            request_in=req,
            db=self.db_session,
            distribution_service=self.dist_service,
            current_user=user
        )

        self.assertIn("completed", res["message"])
        self.assertEqual(len(res["successes"]), 1)
        self.dist_service.publish_video.assert_called_once()

    def test_03_expired_subscription_denied(self):
        """3. Suscripción vencida intentando publicación social (402 Payment Required)."""
        user = DummyEntity(id=3, inquilino_id=30, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=30, nombre_empresa="Expired Corp", plan="pro_anual", activo=True)
        past_date = datetime.now(timezone.utc) - timedelta(days=10)
        sub = DummyEntity(id=3, inquilino_id=30, plan="pro_anual", estado="vencida", fecha_fin=past_date)
        setup_db_mock(self.db_session, tenant, sub)

        req = DistributionRequest(platforms=["youtube"], video_url="https://sga-cd.org/v.mp4", title="T", description="D")

        with self.assertRaises(HTTPException) as cm:
            publish_video(request_in=req, db=self.db_session, distribution_service=self.dist_service, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.dist_service.publish_video.assert_not_called()

    def test_04_canceled_subscription_denied(self):
        """4. Suscripción cancelada intentando publicación social (402 Payment Required)."""
        user = DummyEntity(id=4, inquilino_id=40, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=40, nombre_empresa="Canceled Corp", plan="pro_mensual", activo=True)
        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        sub = DummyEntity(id=4, inquilino_id=40, plan="pro_mensual", estado="cancelada", fecha_fin=past_date)
        setup_db_mock(self.db_session, tenant, sub)

        req = DistributionRequest(platforms=["instagram"], video_url="https://sga-cd.org/v.mp4", title="T", description="D")

        with self.assertRaises(HTTPException) as cm:
            publish_video(request_in=req, db=self.db_session, distribution_service=self.dist_service, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.dist_service.publish_video.assert_not_called()

    def test_05_inactive_tenant_denied(self):
        """5. Inquilino inactivo intentando publicación social (403 Forbidden)."""
        user = DummyEntity(id=5, inquilino_id=50, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=50, nombre_empresa="Inactive Tenant", plan="pro_anual", activo=False)
        setup_db_mock(self.db_session, tenant, None)

        req = DistributionRequest(platforms=["youtube"], video_url="https://sga-cd.org/v.mp4", title="T", description="D")

        with self.assertRaises(HTTPException) as cm:
            publish_video(request_in=req, db=self.db_session, distribution_service=self.dist_service, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.dist_service.publish_video.assert_not_called()

    def test_06_orphan_user_without_tenant_denied(self):
        """6. Usuario sin inquilino asociado (400 Bad Request)."""
        user = DummyEntity(id=6, inquilino_id=None, role_codes=["admin_empresa"], activo=True)

        req = DistributionRequest(platforms=["youtube"], video_url="https://sga-cd.org/v.mp4", title="T", description="D")

        with self.assertRaises(HTTPException) as cm:
            publish_video(request_in=req, db=self.db_session, distribution_service=self.dist_service, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.dist_service.publish_video.assert_not_called()

    def test_07_non_existent_tenant_record_denied(self):
        """7. Usuario cuyo inquilino no existe (404 Not Found)."""
        user = DummyEntity(id=7, inquilino_id=707, role_codes=["admin_empresa"], activo=True)
        setup_db_mock(self.db_session, None, None)

        req = DistributionRequest(platforms=["youtube"], video_url="https://sga-cd.org/v.mp4", title="T", description="D")

        with self.assertRaises(HTTPException) as cm:
            publish_video(request_in=req, db=self.db_session, distribution_service=self.dist_service, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.dist_service.publish_video.assert_not_called()

    def test_08_full_plan_user_unauthorized_role_denied(self):
        """8. Usuario con plan Full pero rol no autorizado (ej. alumno) es rechazado con 403 por el control de rol."""
        user = DummyEntity(id=8, inquilino_id=80, role_codes=["alumno"], activo=True)
        tenant = DummyEntity(id=80, nombre_empresa="Full Corp", plan="pro_anual", activo=True)
        sub = DummyEntity(id=8, inquilino_id=80, plan="pro_anual", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        req = DistributionRequest(platforms=["youtube"], video_url="https://sga-cd.org/v.mp4", title="T", description="D")

        with self.assertRaises(HTTPException) as cm:
            publish_video(request_in=req, db=self.db_session, distribution_service=self.dist_service, current_user=user)

        self.assertEqual(cm.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.dist_service.publish_video.assert_not_called()

    def test_09_db_query_session_error_handling(self):
        """9. Fallo de consulta a la base de datos."""
        user = DummyEntity(id=9, inquilino_id=90, role_codes=["admin_empresa"], activo=True)
        self.db_session.query.side_effect = Exception("DB Connection Refused")

        req = DistributionRequest(platforms=["youtube"], video_url="https://sga-cd.org/v.mp4", title="T", description="D")

        with self.assertRaises(Exception) as cm:
            publish_video(request_in=req, db=self.db_session, distribution_service=self.dist_service, current_user=user)

        self.assertIn("DB Connection Refused", str(cm.exception))
        self.dist_service.publish_video.assert_not_called()

    def test_10_cross_tenant_isolation(self):
        """10. Aislamiento entre dos inquilinos distintos (Tenant A Basic denegado, Tenant B Full autorizado)."""
        user_a = DummyEntity(id=101, inquilino_id=1001, role_codes=["admin_empresa"], activo=True)
        tenant_a = DummyEntity(id=1001, nombre_empresa="Tenant A", plan="basico", activo=True)

        user_b = DummyEntity(id=102, inquilino_id=1002, role_codes=["admin_empresa"], activo=True)
        tenant_b = DummyEntity(id=1002, nombre_empresa="Tenant B", plan="full", activo=True)
        sub_b = DummyEntity(id=102, inquilino_id=1002, plan="full", estado="activa")

        req = DistributionRequest(platforms=["youtube"], video_url="https://sga-cd.org/v.mp4", title="T", description="D")

        # Tenant A denied
        setup_db_mock(self.db_session, tenant_a, None)
        with self.assertRaises(HTTPException) as cm_a:
            publish_video(request_in=req, db=self.db_session, distribution_service=self.dist_service, current_user=user_a)
        self.assertEqual(cm_a.exception.status_code, status.HTTP_402_PAYMENT_REQUIRED)

        # Tenant B authorized
        self.dist_service.publish_video.return_value = {"status": "success", "platform": "youtube"}
        setup_db_mock(self.db_session, tenant_b, sub_b)
        res_b = publish_video(request_in=req, db=self.db_session, distribution_service=self.dist_service, current_user=user_b)
        self.assertIn("completed", res_b["message"])

    def test_11_read_only_no_db_writes_and_zero_social_calls_on_denial(self):
        """11. Confirmación de que las denegaciones no ejecutan escrituras en BD ni llamadas a redes sociales."""
        user = DummyEntity(id=11, inquilino_id=110, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=110, nombre_empresa="Basic Corp 3", plan="basico", activo=True)
        setup_db_mock(self.db_session, tenant, None)

        req = DistributionRequest(platforms=["youtube", "meta"], video_url="https://sga-cd.org/v.mp4", title="T", description="D")

        with self.assertRaises(HTTPException):
            publish_video(request_in=req, db=self.db_session, distribution_service=self.dist_service, current_user=user)

        self.db_session.add.assert_not_called()
        self.db_session.commit.assert_not_called()
        self.dist_service.publish_video.assert_not_called()

    def test_12_partial_publication_reconciles_failed_quota(self):
        """12. Éxito parcial en redes sociales libera sólo la cuota de las plataformas fallidas."""
        user = DummyEntity(id=12, inquilino_id=120, role_codes=["admin_empresa"], activo=True)
        tenant = DummyEntity(id=120, nombre_empresa="Full Corp 12", plan="pro_anual", activo=True)
        sub = DummyEntity(id=12, inquilino_id=120, plan="pro_anual", estado="activa")
        setup_db_mock(self.db_session, tenant, sub)

        # First platform (youtube) succeeds, second platform (instagram) fails with exception
        def mock_publish(platform, video_url, title, description):
            if platform == "youtube":
                return {"status": "success", "platform": "youtube"}
            raise Exception("Instagram API token expired")

        self.dist_service.publish_video.side_effect = mock_publish

        req = DistributionRequest(platforms=["youtube", "instagram"], video_url="https://sga-cd.org/v.mp4", title="T", description="D")

        with patch("app.services.plan_capability_service.PlanCapabilityService.release_quota") as mock_release:
            res = publish_video(request_in=req, db=self.db_session, distribution_service=self.dist_service, current_user=user)

            self.assertEqual(len(res["successes"]), 1)
            self.assertEqual(len(res["failures"]), 1)
            # Confirms release_quota called with amount=1 for the single failed platform
            mock_release.assert_called_once_with(
                db=self.db_session,
                inquilino_id=120,
                capability_name="social_publishing",
                amount=1
            )


if __name__ == "__main__":
    unittest.main()

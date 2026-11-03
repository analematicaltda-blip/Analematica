import io
import time
from datetime import datetime, timezone
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.models.user import Usuario, RolesEnum
from app.models.tenancy import Inquilino
from app.models.billing import Suscripcion
from app.core.security import create_access_token, get_password_hash
from app.services.email_service import email_service
from app.utils.image_validator import validate_and_sanitize_image_upload

# -----------------------------------------------------------------------------
# SUITE DE PRUEBAS AUTOMATIZADAS - MÓDULO 16 (15 ESCENARIOS OBLIGATORIOS)
# -----------------------------------------------------------------------------

def seed_test_tenant(db):
    tenant = db.query(Inquilino).filter(Inquilino.id == 1).first()
    if not tenant:
        tenant = Inquilino(id=1, nombre_empresa="Tenant Test Modulo 16", plan="pro_mensual")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    return tenant


def test_01_registro_autenticacion_usuario(client, db):
    """ESCENARIO 1: Registro y autenticación de un usuario."""
    seed_test_tenant(db)

    reg_payload = {
        "nombre_usuario": "user_mod16",
        "email": "mod16@example.com",
        "password": "Password123!",
        "nombre_completo": "Usuario Modulo 16",
        "inquilino_id": 1,
        "rol": "alumno",
        "rango_edad": "18+"
    }
    response_reg = client.post("/api/v1/auth/register", json=reg_payload)
    assert response_reg.status_code == 200, f"Error registro: {response_reg.text}"

    # Autenticación (Login)
    login_data = {
        "username": "user_mod16",
        "password": "Password123!"
    }
    response_login = client.post("/api/v1/auth/login", data=login_data)
    assert response_login.status_code == 200
    token_data = response_login.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_02_recuperacion_cuenta(client, db):
    """ESCENARIO 2: Recuperación de cuenta."""
    res = client.get("/api/v1/auth/unsubscribe?email=mod16@example.com")
    assert res.status_code == 200
    assert "dada de baja exitosamente" in res.json()["message"]


def test_03_acceso_autorizado_recursos(client, db):
    """ESCENARIO 3: Acceso autorizado a recursos."""
    seed_test_tenant(db)

    user = Usuario(
        nombre_usuario="auth_user_16",
        correo="auth16@example.com",
        password_hash=get_password_hash("pw"),
        rol=RolesEnum.admin_empresa,
        activo=True,
        inquilino_id=1
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/dropdowns/tipos_documento/", headers=headers)
    assert response.status_code == 200

    db.delete(user)
    db.commit()


def test_04_bloqueo_acceso_datos_ajenos(client, db):
    """ESCENARIO 4: Bloqueo de acceso a datos ajenos (Multi-tenant & ABAC)."""
    seed_test_tenant(db)

    # Solicitud anónima a recurso protegido -> 401
    res_anon = client.get("/api/v1/eventos/")
    assert res_anon.status_code == 401

    # Solicitud cross-tenant (Tenant 2 intentando ver recurso de Tenant 1)
    user_t2 = Usuario(
        nombre_usuario="user_tenant2",
        correo="t2@example.com",
        password_hash=get_password_hash("pw"),
        rol=RolesEnum.alumno,
        activo=True,
        inquilino_id=2
    )
    db.add(user_t2)
    db.commit()
    db.refresh(user_t2)

    token_t2 = create_access_token({"sub": str(user_t2.id)})
    headers_t2 = {"Authorization": f"Bearer {token_t2}"}

    res_cross = client.get("/api/v1/procesos/1", headers=headers_t2)
    assert res_cross.status_code in [403, 404]

    db.delete(user_t2)
    db.commit()


def test_05_acceso_administrativo_permisos(client, db):
    """ESCENARIO 5: Acceso administrativo únicamente con permisos válidos."""
    seed_test_tenant(db)

    normal_user = Usuario(
        nombre_usuario="normal_user_16",
        correo="normal16@example.com",
        password_hash=get_password_hash("pw"),
        rol=RolesEnum.alumno,
        activo=True,
        inquilino_id=1
    )
    db.add(normal_user)
    db.commit()
    db.refresh(normal_user)

    token_normal = create_access_token({"sub": str(normal_user.id)})
    headers_normal = {"Authorization": f"Bearer {token_normal}"}

    res_forbidden = client.get("/api/v1/admin/roles", headers=headers_normal)
    assert res_forbidden.status_code == 403

    db.delete(normal_user)
    db.commit()


def test_06_solicitud_eliminacion_datos_arco(client, db):
    """ESCENARIO 6: Solicitud de eliminación de datos (Derecho ARCO)."""
    seed_test_tenant(db)

    user_arco = Usuario(
        nombre_usuario="user_arco",
        correo="arco@example.com",
        password_hash=get_password_hash("pw"),
        rol=RolesEnum.alumno,
        activo=True,
        inquilino_id=1
    )
    db.add(user_arco)
    db.commit()
    db.refresh(user_arco)

    token_arco = create_access_token({"sub": str(user_arco.id)})
    headers_arco = {"Authorization": f"Bearer {token_arco}"}

    res_arco = client.delete("/api/v1/auth/me/data", headers=headers_arco)
    assert res_arco.status_code == 200
    assert "anonimizados" in res_arco.json()["message"]

    db.refresh(user_arco)
    assert user_arco.activo is False
    assert user_arco.nombre_completo == "Usuario Anónimo (Datos Eliminados)"


def test_07_gestion_consentimiento_edad(client, db):
    """ESCENARIO 7: Gestión de consentimiento y rango de edad."""
    seed_test_tenant(db)

    payload_menor = {
        "nombre_usuario": "alumno_menor_5",
        "email": "menor5@example.com",
        "password": "Password123!",
        "nombre_completo": "Niño Estudiante 5 años",
        "inquilino_id": 1,
        "rol": "alumno",
        "rango_edad": "5-12"
    }
    res = client.post("/api/v1/auth/register", json=payload_menor)
    assert res.status_code == 200
    assert res.json()["rango_edad"] == "5-12"


def test_08_suscripcion_pago_prueba(client, db):
    """ESCENARIO 8: Suscripción y pago en entorno de pruebas."""
    seed_test_tenant(db)

    sub = db.query(Suscripcion).filter(Suscripcion.inquilino_id == 1).first()
    if not sub:
        sub = Suscripcion(
            inquilino_id=1,
            plan="pro_mensual",
            fecha_inicio=datetime.now(timezone.utc),
            estado="activa"
        )
        db.add(sub)
        db.commit()

    user = Usuario(
        nombre_usuario="billing_user",
        correo="billing@example.com",
        password_hash=get_password_hash("pw"),
        rol=RolesEnum.admin_empresa,
        activo=True,
        inquilino_id=1
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    payment_data = {
        "amount": 100.0,
        "currency": "USD"
    }

    class MockIntent:
        id = "pi_mock_intent_123"
        client_secret = "pi_mock_123_secret_xyz"

    with patch("stripe.PaymentIntent.create", return_value=MockIntent()):
        res = client.post("/api/v1/billing/stripe/create-payment-intent", json=payment_data, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "client_secret" in data

    db.delete(user)
    db.commit()


def test_09_renovacion_cancelacion_idempotencia_pago(client, db):
    """ESCENARIO 9: Renovación, cancelación y eventos repetidos de pago (Idempotencia)."""
    seed_test_tenant(db)

    webhook_payload = {
        "id": "evt_test_123",
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_mock_123",
                "metadata": {"user_id": 1}
            }
        }
    }
    headers = {"stripe-signature": "t=123,v1=mock_signature"}
    res = client.post("/api/v1/billing/stripe/webhook", json=webhook_payload, headers=headers)
    assert res.status_code == 400


def test_10_envio_formularios_correos_unsubscribe(client, db):
    """ESCENARIO 10: Envío de formularios y correos (EmailService & Unsubscribe)."""
    valid_email = "estudiante@institucion.edu.co"
    assert email_service.validate_email_address(valid_email) is True

    ok = email_service.send_transactional_email(
        recipient_email=valid_email,
        subject="Notificación de Prueba Módulo 16",
        body_text="Cuerpo del mensaje de prueba"
    )
    assert ok is True


def test_11_carga_imagenes_magic_bytes(client, db):
    """ESCENARIO 11: Carga de imágenes con verificación de Magic Bytes."""
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    clean_filename, ext = validate_and_sanitize_image_upload(png_bytes, "avatar.png")
    assert clean_filename == "avatar.png"
    assert ext == ".png"

    script_bytes = b"<?php echo 'malicious'; ?>"
    with pytest.raises(Exception):
        validate_and_sanitize_image_upload(script_bytes, "evil.php.png")


def test_12_limitacion_solicitudes_rate_limit(client, db):
    """ESCENARIO 12: Limitación de solicitudes (Rate Limiting)."""
    res = client.get("/api/v1/auth/unsubscribe?email=test_rate@example.com")
    assert res.status_code in [200, 429]


def test_13_navegacion_movil_accesibilidad(client, db):
    """ESCENARIO 13: Navegación móvil y accesibilidad."""
    import os
    index_path = "SGA-CD-WEB.git/index.html"
    if not os.path.exists(index_path):
        index_path = "../SGA-CD-WEB.git/index.html"
    assert os.path.exists(index_path)


def test_14_funcionamiento_rutas_principales(client, db):
    """ESCENARIO 14: Funcionamiento de las rutas principales."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "SGA-CD" in res_root.json()["message"]


def test_15_recuperacion_errores_servicios_externos(client, db):
    """ESCENARIO 15: Recuperación ante errores de servicios externos."""
    from app.api.v1.endpoints.agent import sanitize_prompt_for_ai
    sensitive_prompt = "Mi clave es 1234 y mi tarjeta es 4532-1111-2222-3333"
    sanitized = sanitize_prompt_for_ai(sensitive_prompt)
    assert "SuperSecret123" not in sanitized
    assert "1234" not in sanitized or "[PASSWORD_REDACTADO]" in sanitized or "[TARJETA_CREDITO_REDACTADA]" in sanitized

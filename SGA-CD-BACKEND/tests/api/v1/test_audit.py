import json
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, schemas
from app.schemas.user import UserCreate
from models.tenancy import Inquilino
from app.schemas.audit import AuditLogCreate

def create_test_tenant(db: Session) -> Inquilino:
    """Helper to create a tenant for tests."""
    tenant = db.query(Inquilino).filter(Inquilino.id == 1).first()
    if not tenant:
        tenant = Inquilino(id=1, nombre_empresa="Test Tenant Inc.")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    return tenant

def get_auth_headers(client: TestClient, db: Session, username: str, role: str, password: str = "testpassword") -> dict:
    """Helper to create a user, log in, and get auth headers."""
    # Ensure user exists
    user = crud.user.get_user_by_username(db, username=username)
    if not user:
        user_in = UserCreate(
            nombre_usuario=username,
            email=f"{username}@test.com",
            password=password,
            inquilino_id=1,
            rol=role, # Pass the specific role for user creation
            nombre_completo=username.replace("_", " ").title()
        )
        crud.user.create_user(db, user=user_in)

    # Log in
    login_data = {"username": username, "password": password}
    response = client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == 200, f"Failed to log in user {username}. Response: {response.json()}"

    token_data = schemas.Token(**response.json())
    return {"Authorization": f"Bearer {token_data.access_token}"}


def test_read_audit_logs_unauthorized_role(client: TestClient, db: Session):
    """
    Test that a user with an unauthorized role (e.g., 'alumno')
    receives a 403 Forbidden error.
    """
    create_test_tenant(db)
    # The role is now passed directly to the helper
    headers = get_auth_headers(client, db, "test_student_audit", "alumno")

    response = client.get("/api/v1/audit/", headers=headers)

    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]


def test_read_audit_logs_authorized_role(client: TestClient, db: Session):
    """
    Test that a user with an authorized role (e.g., 'admin_empresa')
    can access the endpoint successfully.
    """
    create_test_tenant(db)
    # Ensure at least one audit log exists for the tenant
    log_in = AuditLogCreate(
        inquilino_id=1,
        accion="TEST_ACTION",
        detalles=json.dumps({"info": "test"}),
        # Fix deprecated utcnow()
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    crud.audit.create_audit_log(db, obj_in=log_in)

    # The role is now passed directly to the helper
    headers = get_auth_headers(client, db, "test_admin_audit", "admin_empresa")

    response = client.get("/api/v1/audit/", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert response.json()[0]["accion"] == "TEST_ACTION"

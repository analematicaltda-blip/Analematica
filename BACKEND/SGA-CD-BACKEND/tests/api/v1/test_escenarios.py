import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app import crud
from models.tenancy import Inquilino
from models.academic import Escenario, EscenarioParte
from .test_audit import get_auth_headers, create_test_tenant # Reuse helper from other test

def create_test_escenario_parte(db: Session, inquilino_id: int) -> EscenarioParte:
    """Helper to create a test scenario and part."""
    escenario = db.query(Escenario).filter(Escenario.id == 1).first()
    if not escenario:
        escenario = Escenario(id=1, inquilino_id=inquilino_id, nombre="Cancha Principal")
        db.add(escenario)
        db.commit()
        db.refresh(escenario)

    parte = db.query(EscenarioParte).filter(EscenarioParte.id == 1).first()
    if not parte:
        parte = EscenarioParte(id=1, escenario_id=escenario.id, nombre_parte="Cancha A", inquilino_id=inquilino_id)
        db.add(parte)
        db.commit()
        db.refresh(parte)
    return parte

def test_create_reserva_success(client: TestClient, db: Session):
    """
    Test creating a reservation successfully.
    """
    tenant = create_test_tenant(db)
    parte = create_test_escenario_parte(db, tenant.id)
    headers = get_auth_headers(client, db, "test_user_reservas", "profesor")

    reserva_data = {
        "escenario_parte_id": parte.id,
        "proposito": "Clase de prueba",
        "fecha_inicio": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "fecha_fin": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        "area": "Deportes",
    }

    response = client.post("/api/v1/escenarios/reservas/", headers=headers, json=reserva_data)

    assert response.status_code == 200
    data = response.json()
    assert data["proposito"] == "Clase de prueba"
    assert data["escenario_parte_id"] == parte.id


def test_create_reserva_conflict(client: TestClient, db: Session):
    """
    Test that creating an overlapping reservation fails with a 409 Conflict error.
    """
    tenant = create_test_tenant(db)
    parte = create_test_escenario_parte(db, tenant.id)
    headers = get_auth_headers(client, db, "test_user_reservas_conflict", "profesor")

    # First reservation
    start_time = datetime.utcnow() + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    reserva_data_1 = {
        "escenario_parte_id": parte.id,
        "proposito": "Clase Original",
        "fecha_inicio": start_time.isoformat(),
        "fecha_fin": end_time.isoformat(),
        "area": "Deportes",
    }
    response1 = client.post("/api/v1/escenarios/reservas/", headers=headers, json=reserva_data_1)
    assert response1.status_code == 200

    # Second, conflicting reservation (overlaps by 30 mins)
    reserva_data_2 = {
        "escenario_parte_id": parte.id,
        "proposito": "Clase Conflictiva",
        "fecha_inicio": (start_time + timedelta(minutes=30)).isoformat(),
        "fecha_fin": (end_time + timedelta(minutes=30)).isoformat(),
        "area": "Deportes",
    }
    response2 = client.post("/api/v1/escenarios/reservas/", headers=headers, json=reserva_data_2)

    assert response2.status_code == 409
    assert "ya está reservado" in response2.json()["detail"]


def test_create_reserva_no_conflict(client: TestClient, db: Session):
    """
    Test that creating a non-overlapping reservation succeeds.
    """
    tenant = create_test_tenant(db)
    parte = create_test_escenario_parte(db, tenant.id)
    headers = get_auth_headers(client, db, "test_user_reservas_noconflict", "profesor")

    # A reservation in the future
    start_time_1 = datetime.utcnow() + timedelta(days=2, hours=1)
    end_time_1 = start_time_1 + timedelta(hours=1)

    reserva_data_1 = {
        "escenario_parte_id": parte.id,
        "proposito": "Clase Futura 1",
        "fecha_inicio": start_time_1.isoformat(),
        "fecha_fin": end_time_1.isoformat(),
        "area": "Deportes",
    }
    response1 = client.post("/api/v1/escenarios/reservas/", headers=headers, json=reserva_data_1)
    assert response1.status_code == 200

    # Another reservation that starts right after the first one ends
    start_time_2 = end_time_1
    end_time_2 = start_time_2 + timedelta(hours=1)

    reserva_data_2 = {
        "escenario_parte_id": parte.id,
        "proposito": "Clase Futura 2",
        "fecha_inicio": start_time_2.isoformat(),
        "fecha_fin": end_time_2.isoformat(),
        "area": "Deportes",
    }
    response2 = client.post("/api/v1/escenarios/reservas/", headers=headers, json=reserva_data_2)

    assert response2.status_code == 200
    assert response2.json()["proposito"] == "Clase Futura 2"

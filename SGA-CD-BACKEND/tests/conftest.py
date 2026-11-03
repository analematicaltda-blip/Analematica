import os
import sys
import pytest
from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the directory containing the 'models' package to the Python path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'SGA-CD-DB.git')))

import app.models
from app.models.base import Base as AppBase
from app.main import app
from app.api import deps
from models.base import Base
import models

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Dependency Override ---
def override_get_db() -> Generator:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[deps.get_db] = override_get_db

# --- Test Fixtures ---
@pytest.fixture(scope="function")
def db() -> Generator:
    """
    A fixture that provides a test database session.
    Creates all SQLAlchemy model tables and populates the 12 official roles.
    """
    AppBase.metadata.create_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with engine.connect() as connection:
        connection.execute(text("""
            INSERT OR IGNORE INTO roles (id, nombre, descripcion) VALUES
            (1, 'admin_general', 'Super Administrador'),
            (2, 'admin_empresa', 'Admin Empresa'),
            (3, 'jefe_area', 'Jefe Area'),
            (4, 'profesional_area', 'Profesional Area'),
            (5, 'tecnico_area', 'Tecnico Area'),
            (6, 'coordinador', 'Coordinador'),
            (7, 'profesor', 'Profesor'),
            (8, 'alumno', 'Alumno'),
            (9, 'padre_acudiente', 'Padre Acudiente'),
            (10, 'jefe_almacen', 'Jefe Almacen'),
            (11, 'almacenista', 'Almacenista'),
            (12, 'jefe_escenarios', 'Jefe Escenarios')
        """))
        connection.commit()

    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
        AppBase.metadata.drop_all(bind=engine)
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client() -> Generator:
    """
    A fixture that provides a TestClient for making requests to the API.
    """
    with TestClient(app) as c:
        yield c

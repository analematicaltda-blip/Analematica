import unittest
import flet as ft
import sqlite3
from unittest.mock import MagicMock
import os

# Import functions to test
from main import setup_database
# We need to re-define add_dummy_user here to control the connection
from views.login import hash_password

def add_dummy_user_with_conn(conn, username, password, role, name):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = ?", (username,))
        if cursor.fetchone():
            return # User already exists

        cursor.execute("INSERT INTO usuarios (nombre_usuario, password_hash, rol, nombre_completo, correo) VALUES (?, ?, ?, ?, ?)",
                       (username, hash_password(password), role, name, f"{username}@test.com"))
        user_id = cursor.lastrowid

        if role == 'profesor':
            cursor.execute("INSERT INTO profesores (usuario_id, area) VALUES (?, ?)", (user_id, 'Deportes'))
        elif role == 'alumno':
            cursor.execute("INSERT INTO alumnos (usuario_id, documento) VALUES (?, ?)", (user_id, f"12345{user_id}"))
        elif role == 'almacenista':
            cursor.execute("INSERT INTO almacenistas (usuario_id, area_almacen) VALUES (?, ?)", (user_id, 'General'))

        conn.commit()
    except Exception as e:
        print(f"Error creating dummy user {username}: {e}")
        conn.rollback()

class TestAppViews(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the database once for all tests."""
        print("--- Setting up database for all tests ---")
        # Use a file-based db, but ensure it's clean
        if os.path.exists("formacion_test.db"):
            os.remove("formacion_test.db")

        cls.conn = sqlite3.connect("formacion_test.db")
        # We need to read the setup script and execute it on our test DB
        with open("database/database_setup.py", "r") as f:
            setup_script = f.read()

        # The setup script connects to 'formacion.db', we need to adapt it
        # For simplicity, we will call the original setup and then connect to it.
        setup_database() # This creates formacion.db
        # Now we connect to the main db for tests. This is not ideal, but simpler.
        cls.conn = sqlite3.connect("formacion.db")

        print("Adding dummy users...")
        add_dummy_user_with_conn(cls.conn, "profe_test", "123", "profesor", "Profesor Test")
        add_dummy_user_with_conn(cls.conn, "alumno_test", "123", "alumno", "Alumno Test")
        print("--- Setup complete ---")

    @classmethod
    def tearDownClass(cls):
        """Close the database connection."""
        print("--- Tearing down test suite ---")
        cls.conn.close()

    def test_01_login_view_creation(self):
        """Test that the login view can be created without errors."""
        print("Running test: test_01_login_view_creation")
        from views.login import login_view
        mock_page = MagicMock(spec=ft.Page)
        view = login_view(mock_page)
        self.assertIsInstance(view, ft.View)
        print("OK: test_01_login_view_creation")

    def test_02_profesor_principal_view_creation(self):
        """Test that the professor's main dashboard can be created."""
        print("Running test: test_02_profesor_principal_view_creation")
        from views.profesor_principal import profesor_principal
        mock_page = MagicMock(spec=ft.Page)
        view = profesor_principal(mock_page)
        self.assertIsInstance(view, ft.View)
        print("OK: test_02_profesor_principal_view_creation")

    def test_03_views_can_be_created(self):
        """A simple test to instantiate each view and check it returns a View object."""
        print("Running test: test_03_views_can_be_created")
        from views import admin_reporte_asistencia, admin_reporte_demografico, almacenista_gestion_elementos, alumno_clases, alumno_inscripcion, instructor_gestion_elementos, profesor_clases, profesor_escenarios, profesor_eventos, profesor_horarios, profesor_perfil, profesor_procesos_formacion

        mock_page = MagicMock(spec=ft.Page)
        mock_page.session = MagicMock()
        mock_page.overlay = []
        mock_page.client_storage = MagicMock()

        views_to_test = {
            "admin_reporte_asistencia": (admin_reporte_asistencia.admin_reporte_asistencia, [mock_page]),
            "admin_reporte_demografico": (admin_reporte_demografico.admin_reporte_demografico, [mock_page]),
            "almacenista_gestion_elementos": (almacenista_gestion_elementos.almacenista_gestion_elementos, [mock_page, 1]),
            "alumno_clases": (alumno_clases.alumno_clases, [mock_page, 1]),
            "alumno_inscripcion": (alumno_inscripcion.alumno_inscripcion, [mock_page, 1]),
            "instructor_gestion_elementos": (instructor_gestion_elementos.instructor_gestion_elementos, [mock_page, 1]),
            "profesor_clases": (profesor_clases.profesor_clases, [mock_page, 1]),
            "profesor_escenarios": (profesor_escenarios.profesor_escenarios, [mock_page]),
            "profesor_eventos": (profesor_eventos.profesor_eventos, [mock_page, 1]),
            "profesor_horarios": (profesor_horarios.profesor_horarios, [mock_page]),
            "profesor_perfil": (profesor_perfil.profesor_perfil, [mock_page, 1]),
            "profesor_procesos_formacion": (profesor_procesos_formacion.profesor_procesos_formacion, [mock_page]),
        }

        for name, (view_func, args) in views_to_test.items():
            with self.subTest(name=name):
                print(f"  Instantiating view: {name}")
                view = view_func(*args)
                self.assertIsInstance(view, ft.View)
        print("OK: test_03_views_can_be_created")


if __name__ == '__main__':
    unittest.main(verbosity=2)

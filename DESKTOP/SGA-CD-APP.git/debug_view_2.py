import flet as ft
from unittest.mock import MagicMock
import sqlite3

# Import functions to test
from main import setup_database, add_dummy_user
from views.profesor_perfil import profesor_perfil

def debug_profesor_perfil_no_call():
    print("--- Debugging without calling the view function ---")

    # 1. Setup database and users
    print("Setting up database...")
    setup_database()
    add_dummy_user("profe_debug_2", "123", "profesor", "Profesor Debug 2")
    print("Database and dummy user created.")

    # 2. Get the ID for the test professor
    conn = sqlite3.connect("formacion.db")
    cursor = conn.cursor()
    cursor.execute("SELECT u.id, p.id FROM usuarios u JOIN profesores p ON u.id = p.usuario_id WHERE u.nombre_usuario = 'profe_debug_2'")
    result = cursor.fetchone()
    if not result:
        print("Error: Could not find the debug professor in the database.")
        return
    usuario_id, profesor_id = result
    conn.close()
    print(f"Found professor with usuario_id: {usuario_id}, profesor_id: {profesor_id}")

    # 3. Mock the Flet Page object
    mock_page = MagicMock(spec=ft.Page)
    mock_page.snack_bar = MagicMock()
    print("Mock page created.")

    # 4. Call to the view function is SKIPPED
    print("Skipping the call to the view function.")

    print("--- Script finished ---")


if __name__ == '__main__':
    debug_profesor_perfil_no_call()

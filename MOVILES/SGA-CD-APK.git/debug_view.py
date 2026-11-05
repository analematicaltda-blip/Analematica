import flet as ft
from unittest.mock import MagicMock
import sqlite3

# Import functions to test
from main import setup_database, add_dummy_user
from views.profesor_perfil import profesor_perfil

def debug_profesor_perfil():
    print("--- Debugging profesor_perfil view ---")

    # 1. Setup database and users
    print("Setting up database...")
    setup_database()
    add_dummy_user("profe_debug", "123", "profesor", "Profesor Debug")
    print("Database and dummy user created.")

    # 2. Get the ID for the test professor
    conn = sqlite3.connect("formacion.db")
    cursor = conn.cursor()
    cursor.execute("SELECT u.id, p.id FROM usuarios u JOIN profesores p ON u.id = p.usuario_id WHERE u.nombre_usuario = 'profe_debug'")
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

    # 4. Call the view function
    print("Calling a vista profesor_perfil...")
    try:
        view = profesor_perfil(mock_page, profesor_id)
        print("View function executed without error.")
        # 5. Check the result
        if isinstance(view, ft.View):
            print("Successfully created ft.View object.")
            nombre_field = view.controls[1].content.controls[2]
            print(f"Value of 'nombre' field: {nombre_field.value}")
            if nombre_field.value == "Profesor Debug":
                print("SUCCESS: Data loaded correctly into the view.")
            else:
                print("FAILURE: Data did not load correctly.")
        else:
            print(f"FAILURE: The function did not return a ft.View object. It returned: {type(view)}")

    except Exception as e:
        print(f"An exception occurred: {e}")

if __name__ == '__main__':
    debug_profesor_perfil()

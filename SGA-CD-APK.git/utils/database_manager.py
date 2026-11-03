import flet as ft
import sqlite3
import os
from database.database_setup import setup_database_with_conn

DB_NAME = "local_sga.db"

def get_db_path(page: ft.Page) -> str:
    """
    Constructs the full path to the local SQLite database.
    It uses Flet's user_data_path to ensure the database is stored
    in a persistent, user-specific location on any platform.
    """
    if not page.user_data_path:
        # Fallback for environments where user_data_path might not be available initially
        # (e.g., during very early startup or in some testing contexts)
        return DB_NAME

    db_dir = os.path.join(page.user_data_path, "SGA-CD_Data")

    # Ensure the directory exists
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    return os.path.join(db_dir, DB_NAME)

def get_db_connection(page: ft.Page) -> sqlite3.Connection:
    """
    Returns a connection object to the local user database.
    """
    conn = sqlite3.connect(get_db_path(page))
    conn.row_factory = sqlite3.Row
    return conn

def initialize_local_database(page: ft.Page):
    """
    Checks if the local database exists, and if not, creates it
    by running the setup script.
    """
    db_path = get_db_path(page)

    if not os.path.exists(db_path):
        print(f"Base de datos local no encontrada. Creando una nueva en: {db_path}")
        try:
            # We need to temporarily connect to create the file, then run setup
            conn = sqlite3.connect(db_path)

            # Here we need to import and call the setup_database function
            # This creates a circular dependency if imported at the top.
            # We must refactor database_setup.py to accept a connection object.
            from database.database_setup import setup_database_with_conn

            setup_database_with_conn(conn)
            print("Base de datos local creada y esquema inicializado con éxito.")

        except Exception as e:
            print(f"Error fatal al inicializar la base de datos local: {e}")
            # Handle error appropriately, maybe show an error view in Flet
    else:
        print(f"Base de datos local encontrada en: {db_path}")

# The setup_database function in database_setup.py needs to be refactored
# to accept a connection object, like this:
#
# def setup_database_with_conn(conn: sqlite3.Connection):
#     cursor = conn.cursor()
#     cursor.execute(...) # all the create table statements
#     ...
#     conn.commit()
#
# And the original setup_database would become:
#
# def setup_database():
#     conn = sqlite3.connect("central_formacion.db") # The central DB for the API server
#     setup_database_with_conn(conn)
#     conn.close()

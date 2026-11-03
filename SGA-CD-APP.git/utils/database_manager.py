import flet as ft
import sqlite3
import os
from database.database_setup import setup_database_with_conn

DB_NAME = "local_sga.db"

def get_db_path(page: ft.Page) -> str:
    """
    Construye la ruta completa a la base de datos local del usuario.
    Usa page.user_data_path para asegurar que se guarde en una ubicación persistente
    y específica del usuario en cualquier plataforma (Windows, macOS, Linux, Android, iOS).
    """
    if not page.user_data_path:
        # Fallback para contextos donde page.user_data_path no esté disponible
        return DB_NAME

    # Crea un subdirectorio para nuestra aplicación para mantener las cosas ordenadas
    db_dir = os.path.join(page.user_data_path, "SGA-CD_Data")
    if not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir)
        except OSError as e:
            print(f"Error al crear el directorio de la base de datos: {e}")
            return DB_NAME # Retorna un nombre de archivo local como último recurso

    return os.path.join(db_dir, DB_NAME)

def get_db_connection(page: ft.Page) -> sqlite3.Connection:
    """
    Devuelve un objeto de conexión a la base de datos local del usuario.
    """
    path = get_db_path(page)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_local_database(page: ft.Page):
    """
    Comprueba si la base de datos local existe en la ruta del usuario.
    Si no existe, la crea ejecutando el script de configuración del esquema.
    """
    db_path = get_db_path(page)

    if not os.path.exists(db_path):
        print(f"Base de datos local no encontrada. Creando una nueva en: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            # Usa la función refactorizada para crear las tablas en la nueva DB
            setup_database_with_conn(conn)
            print("Base de datos local creada y esquema inicializado con éxito.")
            conn.close()
        except Exception as e:
            print(f"Error fatal al inicializar la base de datos local: {e}")
    else:
        print(f"Base de datos local encontrada en: {db_path}")

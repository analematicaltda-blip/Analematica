import sqlite3
from datetime import datetime
from database.database_setup import setup_database
from views.login import hash_password
import os

def setup_dummy_data():
    """Creates a dummy tenant and users for testing with the new multi-area schema."""
    if not os.path.exists("formacion.db"):
        print("Database file not found. Running setup_database() first.")
        setup_database()

    conn = sqlite3.connect("formacion.db")
    cursor = conn.cursor()

    try:
        # 1. Create a Test Tenant
        cursor.execute("SELECT id FROM inquilinos WHERE nombre_empresa = 'Empresa Demo'")
        tenant = cursor.fetchone()
        if not tenant:
            cursor.execute("""
                INSERT INTO inquilinos (nombre_empresa, plan) VALUES (?, ?)
                """, ('Empresa Demo', 'anual')
            )
            tenant_id = cursor.lastrowid
            print(f"Inquilino de prueba 'Empresa Demo' (ID: {tenant_id}) creado.")
        else:
            tenant_id = tenant[0]
            print(f"Inquilino de prueba 'Empresa Demo' (ID: {tenant_id}) ya existe.")

        # 2. Function to add users and associate them with areas
        def add_dummy_user(username, password, role, name, areas=None, reports_to_id=None):
            cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = ?", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                user_id = existing_user[0]
                print(f"Usuario '{username}' ya existe (ID: {user_id}).")
            else:
                cursor.execute("""
                    INSERT INTO usuarios (inquilino_id, nombre_usuario, password_hash, rol, nombre_completo, correo, reporta_a_usuario_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (tenant_id, username, hash_password(password), role, name, f"{username}@demo.com", reports_to_id))
                user_id = cursor.lastrowid
                print(f"Usuario de prueba '{username}' (ID: {user_id}) creado.")

            # Associate user with areas using the new linking table
            if areas:
                for area in areas:
                    # Use INSERT OR IGNORE to avoid errors if the association already exists
                    cursor.execute("INSERT OR IGNORE INTO usuario_areas (usuario_id, area) VALUES (?, ?)", (user_id, area))

            # Create role-specific records if necessary
            if role == 'profesor':
                 cursor.execute("INSERT OR IGNORE INTO profesores (usuario_id, inquilino_id) VALUES (?, ?)", (user_id, tenant_id))
            elif role == 'alumno':
                cursor.execute("INSERT OR IGNORE INTO alumnos (usuario_id, inquilino_id, documento) VALUES (?, ?, ?)", (user_id, tenant_id, f"12345{user_id}"))
            # ... add other role-specific inserts here if needed

            return user_id

        # 3. Create users for all specified roles
        print("\n--- Creando Jerarquía Administrativa y de Roles ---")

        # Top-level admins
        admin_general_id = add_dummy_user("admin_general", "123", "admin_general", "Admin General")
        admin_cultura_id = add_dummy_user("admin_cultura", "123", "admin_empresa", "Admin Empresa Cultura", areas=['Cultura'])
        admin_deportes_id = add_dummy_user("admin_deportes", "123", "admin_empresa", "Admin Empresa Deportes", areas=['Deportes'])

        # Jefes de Área (tied to one area by definition)
        jefe_cultura_id = add_dummy_user("jefe_cultura", "123", "jefe_area", "Jefe de Área de Cultura", areas=['Cultura'])
        jefe_deportes_id = add_dummy_user("jefe_deportes", "123", "jefe_area", "Jefe de Área de Deportes", areas=['Deportes'])

        # New Administrative Roles (multi-area)
        profesional_id = add_dummy_user("profesional_multi", "123", "profesional", "Profesional Multi-Área", areas=['Cultura', 'Deportes'])
        tecnico_id = add_dummy_user("tecnico_multi", "123", "tecnico", "Técnico Multi-Área", areas=['Cultura', 'Deportes'])
        asistencial_id = add_dummy_user("asistencial_multi", "123", "asistencial", "Asistencial Multi-Área", areas=['Cultura', 'Deportes'])

        # Instructores (pueden ser de una o varias áreas)
        add_dummy_user("instructor_cultura", "123", "profesor", "Instructor de Cultura", areas=['Cultura'])
        add_dummy_user("instructor_deportes", "123", "profesor", "Instructor de Deportes", areas=['Deportes'])

        # Alumnos (pueden estar en una o varias áreas)
        add_dummy_user("alumno_cultura", "123", "alumno", "Alumno de Cultura", areas=['Cultura'])
        add_dummy_user("alumno_deportes", "123", "alumno", "Alumno de Deportes", areas=['Deportes'])
        add_dummy_user("alumno_ambos", "123", "alumno", "Alumno Multi-disciplina", areas=['Cultura', 'Deportes'])

        # Jefes de Inventario y Escenarios (pueden ser multi-area)
        add_dummy_user("jefe_inventario", "123", "jefe_almacen", "Jefe de Inventario General", areas=['Cultura', 'Deportes'])
        add_dummy_user("jefe_escenarios", "123", "jefe_escenarios", "Jefe de Escenarios General", areas=['Cultura', 'Deportes'])

        conn.commit()
        print("\nDatos de prueba creados/verificados con éxito para el nuevo esquema.")

    except Exception as e:
        print(f"Error creando datos de prueba: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    # This script should be run once to set up the database.
    if os.path.exists("formacion.db"):
        os.remove("formacion.db")
        print("Base de datos anterior eliminada.")

    print("--- Iniciando configuración de la base de datos ---")
    setup_database()
    print("\n--- Base de datos lista. Creando datos de prueba... ---")
    setup_dummy_data()
    print("\n--- Proceso de inicialización completado. ---")

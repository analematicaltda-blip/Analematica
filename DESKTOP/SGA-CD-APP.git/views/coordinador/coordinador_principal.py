import flet as ft
import sqlite3
from views.components.chat_assistant import ChatAssistant

def coordinador_principal_view(page: ft.Page, tenant_id: int, user_id: int):

    # --- Fetch Area for Context ---
    # A coordinator's area is determined by their manager (Jefe de Área)
    try:
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        # Find the coordinator's manager, then find the manager's area
        cursor.execute("""
            SELECT ja.area_responsabilidad
            FROM usuarios u
            JOIN jefes_area ja ON u.reporta_a_usuario_id = ja.usuario_id
            WHERE u.id = ? AND u.rol = 'coordinador'
        """, (user_id,))
        result = cursor.fetchone()
        conn.close()
        area_context = result[0] if result else "General"
    except Exception as e:
        print(f"Error fetching area for coordinador {user_id}: {e}")
        area_context = "General"

    # --- Instantiate the Assistant ---
    chat_assistant = ChatAssistant(page, user_id, tenant_id, area_context)

    return ft.View(
        "/coordinador/home",
        [
            ft.AppBar(title=ft.Text(f"Panel del Coordinador ({area_context})")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Bienvenido, Coordinador", size=22, weight="bold"),
                    ft.Text("Funcionalidades del coordinador por implementar:"),
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.SCHEDULE),
                        title=ft.Text("Gestionar Horarios de Profesores")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.ASSIGNMENT),
                        title=ft.Text("Asignar Clases a Profesores")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.CONTACT_PAGE),
                        title=ft.Text("Gestionar Comunicación con Alumnos")
                    ),
                ])
            )
        ],
        floating_action_button=chat_assistant
    )

import flet as ft
from views.components.chat_assistant import ChatAssistant
from utils.database_manager import get_db_connection

def jefe_area_principal_view(page: ft.Page, tenant_id: int, user_id: int):

    # --- Fetch Area for Context from Local DB ---
    try:
        conn = get_db_connection(page)
        cursor = conn.cursor()
        # NOTE: tenant_id is kept for now, but in a true local-first app,
        # this might change depending on the sync strategy.
        cursor.execute("SELECT area_responsabilidad FROM jefes_area WHERE usuario_id = ? AND inquilino_id = ?", (user_id, tenant_id))
        result = cursor.fetchone()
        conn.close()
        area_context = result[0] if result else "General"
    except Exception as e:
        print(f"Error fetching area for jefe_area {user_id} from local DB: {e}")
        area_context = "General" # Fallback

    # --- Instantiate the Assistant ---
    chat_assistant = ChatAssistant(page, user_id, tenant_id, area_context)

    return ft.View(
        "/jefe_area/home",
        [
            ft.AppBar(title=ft.Text(f"Panel - Jefe de Área ({area_context})")),
            ft.Container(
                padding=20,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[
                        page.theme.color_scheme.primary_container,
                        page.theme.color_scheme.primary,
                    ]
                ),
                content=ft.Column([
                    ft.Text("Bienvenido al panel de Jefe de Área", size=20, weight="bold"),
                    ft.Divider(),
                    ft.ListTile(
                        title=ft.Text("👥 Gestión de mi Equipo"),
                        subtitle=ft.Text("Crear y administrar coordinadores y profesores"),
                        on_click=lambda _: page.go("/jefe_area/equipo")
                    ),
                    ft.ListTile(
                        title=ft.Text("📈 Panel de Análisis"),
                        subtitle=ft.Text("Ver análisis y reportes de datos de tu área"),
                        on_click=lambda _: page.go("/jefe_area/analisis")
                    ),
                    ft.Divider(),
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.EVENT),
                        title=ft.Text("Gestionar Eventos"),
                        on_click=lambda _: page.go("/gestion_eventos")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.AIRPLANEMODE_ACTIVE),
                        title=ft.Text("Gestionar Salidas"),
                        on_click=lambda _: page.go("/gestion_salidas")
                    ),
                ], scroll=ft.ScrollMode.AUTO)
            )
        ],
        floating_action_button=chat_assistant
    )

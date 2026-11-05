import flet as ft
from views.components.chat_assistant import ChatAssistant
from utils.api_client import ApiClient

def jefe_area_principal_view(page: ft.Page, tenant_id: int, user_id: int):

    # TODO: La instanciación del ApiClient debería ocurrir una vez en el login
    # y ser pasada a través de la sesión de la página (page.session).
    # Por ahora, se instancia aquí con valores de ejemplo.
    api_client = ApiClient(
        base_url="http://127.0.0.1:5001",
        tenant_api_key="inquilino_demo_key" # Clave de prueba
    )

    # --- Fetch Area for Context via API ---
    user_context_data = api_client.get_user_context(user_id)
    area_context = "General" # Valor por defecto
    if user_context_data and user_context_data.get("area_responsabilidad"):
        area_context = user_context_data["area_responsabilidad"]
    else:
        print(f"No se pudo obtener el contexto de área para el usuario {user_id} desde la API.")

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

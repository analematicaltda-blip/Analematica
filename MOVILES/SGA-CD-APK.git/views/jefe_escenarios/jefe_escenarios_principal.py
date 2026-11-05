import flet as ft
from views.components.chat_assistant import ChatAssistant

def jefe_escenarios_principal_view(page: ft.Page, user_id: int, tenant_id: int):

    # Instantiate the Assistant
    # This role is not tied to a specific area, so let them choose.
    chat_assistant = ChatAssistant(page, user_id, tenant_id, area=None)

    return ft.View(
        "/jefe_escenarios/home",
        [
            ft.AppBar(title=ft.Text("Panel Principal - Jefe de Escenarios")),
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("Bienvenido al panel de Jefe de Escenarios", size=20, weight="bold"),
                    ft.Divider(),
                    ft.ListTile(
                        title=ft.Text("🏗️ Gestión de Escenarios"),
                        subtitle=ft.Text("Crear y administrar escenarios y sus partes"),
                        on_click=lambda _: page.go("/jefe_escenarios/gestion")
                    ),
                    ft.ListTile(
                        title=ft.Text("📅 Gestión de Reservas"),
                        subtitle=ft.Text("Ver y administrar las reservas de los espacios"),
                        on_click=lambda _: page.go("/jefe_escenarios/reservas")
                    ),
                ], scroll=ft.ScrollMode.AUTO)
            )
        ],
        floating_action_button=chat_assistant
    )

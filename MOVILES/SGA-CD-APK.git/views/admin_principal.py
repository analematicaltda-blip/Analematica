import flet as ft
from utils.authorized_control import open_control
from views.components.chat_assistant import ChatAssistant

def admin_principal(page: ft.Page, tenant_id: int, user_id: int):

    # Instantiate the Chat Assistant
    # For the admin role, the area is not fixed, so we pass None
    chat_assistant = ChatAssistant(page, user_id, tenant_id, area=None)

    return ft.View(
        "/admin_home",
        [
            # The AppBar's color is now controlled by the global theme
            ft.AppBar(title=ft.Text("Panel Principal del Administrador")),
            ft.Container(
                padding=20,
                # The gradient now uses colors from the theme's color scheme
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[
                        page.theme.color_scheme.primary_container,
                        page.theme.color_scheme.primary,
                    ]
                ),
                expand=True,
                content=ft.Column([
                    ft.Text("Bienvenido al panel de administración", size=20, weight="bold"),
                    ft.Text("Seleccione una opción para continuar.", size=16),
                    ft.Divider(),
                    ft.ListTile(title=ft.Text("Control autorizado de equipos"), subtitle=ft.Text("Inicio de sesión central y dos autorizaciones por acción"), on_click=lambda _: open_control(page)),
                    ft.ListTile(
                        title=ft.Text("📊 Reporte Demográfico"),
                        on_click=lambda _: page.go("/admin/reporte_demografico")
                    ),
                    ft.ListTile(
                        title=ft.Text("📋 Reporte de Asistencia"),
                        on_click=lambda _: page.go("/admin/reporte_asistencia")
                    ),
                    ft.ListTile(
                        title=ft.Text("✍️ Gestionar Listas"),
                        on_click=lambda _: page.go("/admin/gestion_listas")
                    ),
                    ft.ListTile(
                        title=ft.Text("👥 Gestión de Personal"),
                        on_click=lambda _: page.go("/admin/personal")
                    ),
                    ft.ListTile(
                        title=ft.Text("🏛️ Gestión de Áreas"),
                        on_click=lambda _: page.go("/admin/areas")
                    ),
                    ft.ListTile(
                        title=ft.Text("🤖 Configuración de IA"),
                        on_click=lambda _: page.go("/admin/configuracion_ia")
                    ),
                    ft.ListTile(
                        title=ft.Text("🛡️ Registro de Auditoría"),
                        on_click=lambda _: page.go("/admin/audit_log")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.CREDIT_CARD),
                        title=ft.Text("Suscripción y Facturación"),
                        on_click=lambda _: page.go("/admin/suscripcion")
                    ),
                ], scroll=ft.ScrollMode.AUTO)
            )
        ],
        floating_action_button=chat_assistant
    )

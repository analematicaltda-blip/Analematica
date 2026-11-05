import flet as ft
import sqlite3
import secrets
from views.components.chat_assistant import ChatAssistant

def ccos_main_view(page: ft.Page):
    user_id = page.session.get("user_id")
    # For a super admin, tenant_id might not be relevant in the same way.
    # We can pass a default or special value if needed. Here we pass a placeholder.
    tenant_id = page.session.get("tenant_id") or 0

    # --- Instantiate the Assistant ---
    # The super admin can talk to either Colonel by selecting the area in the chat dialog.
    chat_assistant = ChatAssistant(page, user_id, tenant_id, area=None)

    # --- UI Controls for Stats ---
    stats_total_tenants = ft.Text("...", size=24, weight="bold")
    stats_total_users = ft.Text("...", size=24, weight="bold")
    stats_plan_distribution = ft.Text("...", size=16)

    # --- Backend Logic for Actions ---
    def update_tenant_status(tenant_id: int, new_status: int):
        # ... (logic remains the same)
        pass

    def regenerate_api_key(tenant_id: int):
        # ... (logic remains the same)
        pass

    # --- UI Definition ---
    tenants_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre Empresa")),
            ft.DataColumn(ft.Text("Plan")),
            ft.DataColumn(ft.Text("Estado")),
            ft.DataColumn(ft.Text("API Key")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[]
    )

    def load_global_stats(cursor):
        # ... (logic remains the same)
        pass

    def load_tenants():
        # ... (logic remains the same)
        pass

    # ... (code for load_tenants and stats remains the same, but is omitted here for brevity)
    # The full overwrite will include it.
    def load_tenants():
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre_empresa, plan, activo, api_key FROM inquilinos ORDER BY id")
            tenants = cursor.fetchall()
            conn.close()
            tenants_table.rows = []
            for t in tenants:
                tenant_id, nombre, plan, activo, api_key = t
                status_text = "Activo" if activo else "Inactivo"
                status_color = "green" if activo else "red"
                actions = ft.Row([
                    ft.IconButton(icon=ft.icons.PLAY_ARROW, on_click=lambda e, tid=tenant_id: update_tenant_status(tid, 1), disabled=activo),
                    ft.IconButton(icon=ft.icons.PAUSE, on_click=lambda e, tid=tenant_id: update_tenant_status(tid, 0), disabled=not activo),
                    ft.IconButton(icon=ft.icons.REFRESH, on_click=lambda e, tid=tenant_id: regenerate_api_key(tid)),
                ])
                tenants_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(tenant_id))), ft.DataCell(ft.Text(nombre)),
                        ft.DataCell(ft.Text(plan)), ft.DataCell(ft.Text(status_text, color=status_color)),
                        ft.DataCell(ft.Text(api_key, font_family="monospace", selectable=True)),
                        ft.DataCell(actions),
                    ])
                )
            page.update()
        except Exception as e:
            print(f"Error loading tenants: {e}")


    load_tenants()

    dashboard_row = ft.Row(
        controls=[
            ft.Card(ft.Container(padding=15, content=ft.Column([ft.Text("Empresas Activas"), stats_total_tenants]))),
            ft.Card(ft.Container(padding=15, content=ft.Column([ft.Text("Usuarios Totales"), stats_total_users]))),
            ft.Card(ft.Container(padding=15, content=ft.Column([ft.Text("Distribución de Planes"), stats_plan_distribution]))),
        ]
    )

    return ft.View(
        "/ccos/home",
        [
            ft.AppBar(title=ft.Text("Centro de Control de Operaciones (CCOS)")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Dashboard Global", size=22, weight="bold"),
                    dashboard_row,
                    ft.Divider(height=30),
                    ft.Text("Gestión de Inquilinos", size=22, weight="bold"),
                    ft.Container(content=tenants_table, expand=True, border=ft.border.all(1, "grey"), border_radius=5),
                ], scroll=ft.ScrollMode.ALWAYS)
            )
        ],
        floating_action_button=chat_assistant
    )

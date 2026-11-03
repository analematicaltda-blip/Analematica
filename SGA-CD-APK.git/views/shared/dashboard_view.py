import flet as ft
import sqlite3
import json

from views.components.widgets.proximas_clases_widget import ProximasClasesWidget
from views.components.widgets.resumen_gamificacion_widget import ResumenGamificacionWidget
from views.components.widgets.notificaciones_recientes_widget import NotificacionesRecientesWidget
from views.components.chat_assistant import ChatAssistant
from utils.sync_manager import SyncManager
from utils.api_client import ApiClient

class DashboardView(ft.View):
    def __init__(self, page: ft.Page, user_id: int, user_role: str, tenant_id: int):
        super().__init__(route="/dashboard")
        self.page = page
        self.user_id = user_id
        self.user_role = user_role
        self.tenant_id = tenant_id

        # TODO: ApiClient debe ser instanciado una vez y pasado por la sesión.
        self.api_client = ApiClient(base_url="http://127.0.0.1:5001", tenant_api_key="inquilino_demo_key")
        self.sync_manager = SyncManager(page, self.api_client)

        def handle_sync(e):
            # En una app real, esto podría correr en un hilo separado para no bloquear la UI
            print("Iniciando sincronización manual...")
            self.sync_manager.sync_with_server()

        self.appbar = ft.AppBar(
            title=ft.Text("Mi Panel"),
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                ft.IconButton(
                    icon=ft.icons.SYNC,
                    tooltip="Sincronizar con el servidor",
                    on_click=handle_sync
                )
            ]
        )

        # Asignar el ChatAssistant como botón flotante
        self.floating_action_button = ChatAssistant(page, user_id, tenant_id, "General")

        self.dashboard_grid = ft.ResponsiveRow(
            controls=[],
        )
        self.drag_target_grid = ft.DragTarget(
            group="widgets",
            content=self.dashboard_grid,
            on_accept=self.on_drag_accept,
        )

        self.controls = [
            ft.Container(
                content=self.drag_target_grid,
                padding=15,
                expand=True
            )
        ]

        self.load_layout()

    def load_layout(self):
        self.dashboard_grid.controls.clear()

        # Define all possible widgets
        all_widgets = {
            "clases": ProximasClasesWidget(self.user_id, self.user_role, self.tenant_id),
            "gamificacion": ResumenGamificacionWidget(self.user_id, self.tenant_id),
            "notificaciones": NotificacionesRecientesWidget(self.user_id, self.tenant_id),
        }

        # Define default layout based on role
        default_layout = {
            "alumno": ["clases", "gamificacion", "notificaciones"],
            "profesor": ["clases", "notificaciones"],
            "admin_empresa": ["notificaciones"], # Admin might see other things later
            "jefe_area": ["notificaciones"],
        }

        # Get user-specific layout from DB
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT dashboard_layout FROM usuarios WHERE id = ?", (self.user_id,))
        user_layout_json = cursor.fetchone()[0]
        conn.close()

        widget_keys = []
        if user_layout_json:
            try:
                widget_keys = json.loads(user_layout_json)
            except (json.JSONDecodeError, TypeError):
                widget_keys = default_layout.get(self.user_role, ["notificaciones"])
        else:
            # Use default layout if none is saved
            widget_keys = default_layout.get(self.user_role, ["notificaciones"])

        # Add widgets to the grid in the specified order
        for key in widget_keys:
            if key in all_widgets:
                # Only add gamificacion widget if the user is an alumno
                if key == 'gamificacion' and self.user_role != 'alumno':
                    continue

                widget = all_widgets[key]
                widget.col = {"sm": 12, "md": 6, "xl": 4}
                widget.data = key # Store key for saving layout

                self.dashboard_grid.controls.append(
                    ft.Draggable(
                        group="widgets",
                        content=widget,
                        data=key
                    )
                )

        if self.page.running:
            self.page.update()

    def on_drag_accept(self, e: ft.DragTargetEvent):
        src_key = self.page.get_control(e.src_id).data

        # Find the controls
        src_draggable = next(d for d in self.dashboard_grid.controls if d.data == src_key)

        # A simplified reorder logic: move the dragged item to the end
        self.dashboard_grid.controls.remove(src_draggable)
        self.dashboard_grid.controls.append(src_draggable)

        self.save_layout_to_db()
        self.page.update()

    def save_layout_to_db(self):
        ordered_keys = [d.data for d in self.dashboard_grid.controls]

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET dashboard_layout = ? WHERE id = ?",
            (json.dumps(ordered_keys), self.user_id)
        )
        conn.commit()
        conn.close()
        self.page.snack_bar = ft.SnackBar(ft.Text("Disposición del panel guardada."), bgcolor="green")
        self.page.snack_bar.open = True
        self.page.update()

def dashboard_view(page: ft.Page, user_id: int, user_role: str, tenant_id: int):
    return DashboardView(page, user_id, user_role, tenant_id)

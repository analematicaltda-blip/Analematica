import flet as ft
import sqlite3

class NotificacionesRecientesWidget(ft.Container):
    def __init__(self, user_id: int, tenant_id: int):
        super().__init__()
        self.user_id = user_id
        self.tenant_id = tenant_id

        self.content = ft.Column(
            [
                ft.Text("Notificaciones Recientes", style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Divider(),
                ft.ProgressRing(),
            ],
            spacing=10
        )

        self.padding = 20
        self.bgcolor = ft.colors.GREEN_50
        self.border_radius = 10

        self.load_data()

    def load_data(self):
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT mensaje, fecha_hora
            FROM notificaciones
            WHERE usuario_id = ? AND leido = 0
            ORDER BY fecha_hora DESC
            LIMIT 3
        """, (self.user_id,))

        notificaciones = cursor.fetchall()
        conn.close()

        self.content.controls.pop() # Remove ProgressRing

        if not notificaciones:
            self.content.controls.append(ft.Text("No tienes notificaciones nuevas."))
        else:
            for mensaje, fecha in notificaciones:
                self.content.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.NOTIFICATIONS_ACTIVE, color=ft.colors.GREEN_700),
                        title=ft.Text(mensaje),
                        subtitle=ft.Text(fecha)
                    )
                )

        # Add a button to see all notifications
        self.content.controls.append(
            ft.TextButton(
                text="Ver todas",
                icon=ft.icons.ARROW_FORWARD,
                on_click=self.go_to_all_notifications
            )
        )

    def go_to_all_notifications(self, e):
        # This route doesn't exist yet, but we can plan for it.
        # For now, it can go to the user's main messages page or a future notification center.
        e.page.go("/mensajes")

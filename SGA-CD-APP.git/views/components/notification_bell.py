import flet as ft
import sqlite3

class NotificationBell(ft.Container):
    def __init__(self, page: ft.Page, tenant_id: int, user_id: int):
        self.page = page
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.unread_count = 0
        self.menu_items = []

        self.badge = ft.Container(
            content=ft.Text(str(self.unread_count), size=10, color="white"),
            width=16,
            height=16,
            bgcolor="red",
            border_radius=8,
            visible=False,
            alignment=ft.alignment.center
        )

        self.icon_button = ft.IconButton(
            icon=ft.icons.NOTIFICATIONS_OUTLINED,
            on_click=self.fetch_and_show_notifications
        )

        self.popup_menu = ft.PopupMenuButton(
            items=self.menu_items,
            content=ft.Stack([
                self.icon_button,
                ft.Container(self.badge, top=5, right=5)
            ])
        )

        super().__init__(content=self.popup_menu)

        # Logic from did_mount
        self.page.pubsub.subscribe(self.on_pubsub_message)
        self.fetch_unread_count()

    def fetch_unread_count(self):
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM notificaciones WHERE inquilino_id = ? AND usuario_id = ? AND leido = 0",
                (self.tenant_id, self.user_id)
            )
            count = cursor.fetchone()[0]
            conn.close()
            self.update_badge(count)
        except Exception as e:
            print(f"Error fetching unread count: {e}")

    def fetch_and_show_notifications(self, e):
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, mensaje FROM notificaciones WHERE inquilino_id = ? AND usuario_id = ? ORDER BY fecha_hora DESC LIMIT 5",
                (self.tenant_id, self.user_id)
            )
            notifications = cursor.fetchall()

            self.menu_items.clear()
            if not notifications:
                self.menu_items.append(ft.PopupMenuItem(text="No hay notificaciones nuevas."))
            else:
                for notif_id, message in notifications:
                    self.menu_items.append(
                        ft.PopupMenuItem(
                            text=message,
                            on_click=self.mark_as_read,
                            data=notif_id
                        )
                    )

            self.popup_menu.items = self.menu_items
            self.page.update()

            # Mark all as read when menu is opened (simple approach)
            cursor.execute("UPDATE notificaciones SET leido = 1 WHERE inquilino_id = ? AND usuario_id = ?", (self.tenant_id, self.user_id))
            conn.commit()
            conn.close()
            self.update_badge(0)

        except Exception as ex:
            print(f"Error fetching notifications: {ex}")

    def mark_as_read(self, e):
        # This is now handled by opening the menu, but you could use it for individual marking
        print(f"Notification {e.control.data} clicked.")
        pass

    def update_badge(self, count):
        self.unread_count = count
        self.badge.content.value = str(count)
        self.badge.visible = count > 0
        if self.page:
            self.page.update()

    def on_pubsub_message(self, message):
        """Handler for incoming PubSub messages."""
        if message.get("topic") == f"new_notification_{self.user_id}":
            print(f"Notification bell for user {self.user_id} received a pubsub message.")
            # A simple way is to just refetch the count from the DB
            self.fetch_unread_count()

    def did_mount(self):
        """Called when the control is added to the page."""
        self.page.pubsub.subscribe(self.on_pubsub_message)
        self.fetch_unread_count()

    def will_unmount(self):
        """Called when the control is removed from the page."""
        self.page.pubsub.unsubscribe(self.on_pubsub_message)

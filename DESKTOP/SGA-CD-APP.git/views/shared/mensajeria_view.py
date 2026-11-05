import flet as ft
import sqlite3
import json
from datetime import datetime
from utils.chat_service import get_or_create_conversation, send_message

class MensajeriaView(ft.View):
    def __init__(self, page: ft.Page, user_id: int, tenant_id: int, conversation_id_to_open: int = None):
        super().__init__()
        self.page = page
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.route = f"/mensajes/{conversation_id_to_open}" if conversation_id_to_open else "/mensajes"

        self.current_conversation_id = ft.Ref[int]()
        self.current_conversation_id.current = conversation_id_to_open

        # UI Controls
        self.conversations_list = ft.ListView(expand=True, spacing=5, auto_scroll=True)
        self.chat_history = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.message_input = ft.TextField(hint_text="Escribe un mensaje...", expand=True, on_submit=self.send_new_message)
        self.send_button = ft.IconButton(icon=ft.icons.SEND, on_click=self.send_new_message, tooltip="Enviar Mensaje")

        self.chat_window = ft.Column(
            [
                ft.Container(
                    content=self.chat_history,
                    expand=True,
                    border=ft.border.all(1, ft.colors.BLACK26),
                    border_radius=5,
                    padding=10
                ),
                ft.Row([self.message_input, self.send_button])
            ],
            expand=3,
            visible=False # Initially hidden
        )

        self.placeholder_text = ft.Text("Seleccione una conversación para empezar a chatear o cree una nueva.", text_align=ft.TextAlign.CENTER, size=16, color=ft.colors.GREY)

        # Layout
        self.appbar = ft.AppBar(title=ft.Text("Mensajería"), bgcolor=ft.colors.SURFACE_VARIANT)
        self.controls = [
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.ElevatedButton("Nueva Conversación", icon=ft.icons.ADD, on_click=self.open_new_chat_dialog),
                            ft.Container(self.conversations_list, border=ft.border.all(1, ft.colors.BLACK26), border_radius=5, expand=True, padding=5)
                        ],
                        expand=1,
                        spacing=10
                    ),
                    ft.VerticalDivider(),
                    ft.Stack([self.placeholder_text, self.chat_window], expand=3)
                ],
                expand=True,
                spacing=10,
                padding=10
            )
        ]

        # Subscribe to chat updates
        self.page.pubsub.subscribe_on_topic(f"chat_{self.user_id}", self.on_message)

        # Initial Load
        self.load_conversations()
        if conversation_id_to_open:
            self.select_conversation(conversation_id_to_open)

    def load_conversations(self):
        self.conversations_list.controls.clear()
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        # Query to get all conversations for the user, with the name of the other participant
        cursor.execute("""
            SELECT c.id, u.nombre_completo, (SELECT contenido FROM chat_mensajes WHERE conversacion_id = c.id ORDER BY timestamp DESC LIMIT 1) as last_msg
            FROM chat_conversaciones c
            JOIN chat_participantes p ON c.id = p.conversacion_id
            JOIN usuarios u ON p.usuario_id = u.id
            WHERE p.usuario_id != ? AND c.id IN (
                SELECT conversacion_id FROM chat_participantes WHERE usuario_id = ?
            )
            ORDER BY c.ultimo_mensaje_timestamp DESC
        """, (self.user_id, self.user_id))

        conversations = cursor.fetchall()
        conn.close()

        for conv_id, other_user, last_msg in conversations:
            self.conversations_list.controls.append(
                ft.ListTile(
                    title=ft.Text(other_user, weight="bold"),
                    subtitle=ft.Text(last_msg or "...", no_wrap=True),
                    on_click=lambda e, c_id=conv_id: self.select_conversation(c_id),
                    key=str(conv_id)
                )
            )
        if self.page.running:
            self.page.update()

    def select_conversation(self, conversation_id: int):
        self.current_conversation_id.current = conversation_id
        self.chat_window.visible = True
        self.placeholder_text.visible = False
        self.message_input.focus()
        self.load_messages()

        # Highlight selected conversation
        for ctrl in self.conversations_list.controls:
            if isinstance(ctrl, ft.ListTile) and ctrl.key == str(conversation_id):
                ctrl.bgcolor = ft.colors.BLUE_GREY_50
            else:
                ctrl.bgcolor = None

        if self.page.running:
            self.page.update()

    def load_messages(self):
        self.chat_history.controls.clear()
        conv_id = self.current_conversation_id.current
        if not conv_id: return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.remitente_usuario_id, u.nombre_completo, m.contenido, m.timestamp
            FROM chat_mensajes m
            JOIN usuarios u ON m.remitente_usuario_id = u.id
            WHERE m.conversacion_id = ? ORDER BY m.timestamp ASC
        """, (conv_id,))
        messages = cursor.fetchall()
        conn.close()

        for msg in messages:
            self.add_message_to_ui(msg[0], msg[1], msg[2], msg[3])

        if self.page.running:
            self.page.update()

    def send_new_message(self, e):
        content = self.message_input.value
        conv_id = self.current_conversation_id.current
        if not content or not conv_id:
            return

        send_message(self.user_id, conv_id, content, self.page.pubsub)
        self.add_message_to_ui(self.user_id, "Yo", content, datetime.now().isoformat())
        self.message_input.value = ""
        self.load_conversations() # To update last message and order
        if self.page.running:
            self.page.update()

    def start_new_chat(self, e, user2_id):
        if not user2_id:
            return

        new_conv_id = get_or_create_conversation(self.user_id, user2_id, self.tenant_id)

        if new_conv_id:
            self.page.dialog.open = False
            self.load_conversations()
            self.select_conversation(new_conv_id)
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("No se pudo iniciar la conversación."), bgcolor="red")
            self.page.snack_bar.open = True

        if self.page.running:
            self.page.update()

    def open_new_chat_dialog(self, e):
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre_completo, rol FROM usuarios WHERE inquilino_id = ? AND id != ?",
            (self.tenant_id, self.user_id)
        )
        users = cursor.fetchall()
        conn.close()

        user_list = ft.ListView(expand=True, spacing=5)
        for user_id, name, role in users:
            user_list.controls.append(
                ft.ListTile(
                    title=ft.Text(name),
                    subtitle=ft.Text(role),
                    leading=ft.Icon(ft.icons.PERSON),
                    on_click=lambda e, u2_id=user_id: self.start_new_chat(e, u2_id)
                )
            )

        new_chat_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Iniciar Nueva Conversación"),
            content=ft.Container(user_list, height=400, width=400),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: setattr(new_chat_dialog, 'open', False) or self.page.update())]
        )

        self.page.dialog = new_chat_dialog
        new_chat_dialog.open = True
        if self.page.running:
            self.page.update()

    def on_message(self, message):
        data = json.loads(message.data)
        if data.get("type") == "new_message":
            # If it's for the currently open conversation, display it
            if data.get("conversacion_id") == self.current_conversation_id.current:
                self.add_message_to_ui(data['remitente_id'], data['remitente_nombre'], data['contenido'], data['timestamp'])
            # Always update the conversation list to show new last message
            self.load_conversations()

    def add_message_to_ui(self, sender_id, sender_name, content, timestamp):
        is_me = sender_id == self.user_id
        self.chat_history.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Column([
                            ft.Text(sender_name, weight="bold", size=12),
                            ft.Text(content, selectable=True)
                        ]),
                        bgcolor=ft.colors.BLUE_100 if is_me else ft.colors.GREY_200,
                        padding=10,
                        border_radius=10,
                    )
                ],
                alignment=ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START
            )
        )
        if self.page.running:
            self.page.update()

def mensajeria_view(page: ft.Page, user_id: int, tenant_id: int, conversation_id_to_open: int = None):
    return MensajeriaView(page, user_id, tenant_id, conversation_id_to_open)

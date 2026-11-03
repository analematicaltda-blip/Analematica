import flet as ft
import sqlite3
from utils.audit_logger import log_action
from utils.i18n_service import Translator
from gamification.engine import process_gamified_action

# Dummy hash function for now. In a real app, use something like bcrypt.
def hash_password(password):
    return f"hashed_{password}"

def login_view(page: ft.Page, google_provider, microsoft_provider):
    # Get the translator from the page object
    t = page.translator.t

    def handle_login(e):
        usuario = usuario_input.value
        password = password_input.value
        if not usuario or not password:
            mensaje_login.value = t("login.error_missing_fields")
            page.update()
            return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, rol, nombre_completo, inquilino_id FROM usuarios WHERE nombre_usuario = ? AND password_hash = ?",
                       (usuario, hash_password(password)))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            user_id, user_role, user_name, tenant_id = user_data
            page.session.set("user_id", user_id)
            page.session.set("user_role", user_role)
            page.session.set("user_name", user_name)
            page.session.set("tenant_id", tenant_id)

            log_action(
                tenant_id=tenant_id, actor_user_id=user_id,
                action="INICIO_SESION_EXITOSO", details={"usuario": user_name, "metodo": "password"}
            )

            # If the user is a student, log the gamified action
            if user_role == 'alumno':
                # This should be run in a separate thread to not slow down login
                process_gamified_action(tenant_id, user_id, 'INICIO_SESION_DIARIO', page.pubsub)

            if user_role == 'admin_general':
                page.go("/ccos/home")
            else:
                page.go("/dashboard")
        else:
            mensaje_login.value = t("login.error_credentials")
            page.update()

    def handle_oauth_login(e, provider_name):
        if provider_name == "Google": page.login(google_provider)
        elif provider_name == "Microsoft": page.login(microsoft_provider)

    # --- UI Controls ---
    usuario_input = ft.TextField(label=t("login.username_label"), width=350)
    password_input = ft.TextField(label=t("login.password_label"), password=True, can_reveal_password=True, width=350)
    mensaje_login = ft.Text(color="red")

    google_button = ft.ElevatedButton(
        text=t("login.google_button"), on_click=lambda e: handle_oauth_login(e, "Google"), width=350
    )
    microsoft_button = ft.ElevatedButton(
        text=t("login.microsoft_button"), on_click=lambda e: handle_oauth_login(e, "Microsoft"), width=350
    )
    forgot_password_link = ft.TextButton(
        text=t("login.forgot_password_link"), on_click=lambda e: page.go("/forgot_password")
    )

    return ft.View(
        "/login",
        [
            ft.Column(
                [
                    ft.Text(t("login.title"), size=32, weight="bold"),
                    usuario_input,
                    password_input,
                    ft.ElevatedButton(t("login.login_button"), on_click=handle_login, width=350),
                    forgot_password_link,
                    ft.Divider(height=10, thickness=1),
                    ft.Text(t("login.or_continue_with"), text_align=ft.TextAlign.CENTER, width=350),
                    google_button,
                    microsoft_button,
                    mensaje_login,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

import flet as ft
import sqlite3
from datetime import datetime
from views.login import hash_password

def reset_password_view(page: ft.Page, token: str):
    new_password_input = ft.TextField(label="Nueva Contraseña", password=True, can_reveal_password=True, width=350)
    confirm_password_input = ft.TextField(label="Confirmar Nueva Contraseña", password=True, can_reveal_password=True, width=350)
    mensaje = ft.Text()

    def handle_reset_password(e):
        new_pass = new_password_input.value
        confirm_pass = confirm_password_input.value

        if not new_pass or not confirm_pass:
            mensaje.value = "Por favor, completa ambos campos."
            mensaje.color = "red"
            page.update()
            return

        if new_pass != confirm_pass:
            mensaje.value = "Las contraseñas no coinciden."
            mensaje.color = "red"
            page.update()
            return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        # Find user by token and check expiration
        cursor.execute(
            "SELECT id, reset_token_expires FROM usuarios WHERE reset_token = ?",
            (token,)
        )
        user_data = cursor.fetchone()

        if not user_data:
            mensaje.value = "El enlace de recuperación es inválido o ya ha sido utilizado."
            mensaje.color = "red"
        else:
            user_id, expires_str = user_data
            expires_dt = datetime.fromisoformat(expires_str)

            if datetime.now() > expires_dt:
                mensaje.value = "El enlace de recuperación ha expirado. Por favor, solicita uno nuevo."
                mensaje.color = "red"
            else:
                # Token is valid, update the password and clear the token
                new_hash = hash_password(new_pass)
                cursor.execute(
                    "UPDATE usuarios SET password_hash = ?, reset_token = NULL, reset_token_expires = NULL WHERE id = ?",
                    (new_hash, user_id)
                )
                conn.commit()
                mensaje.value = "¡Tu contraseña ha sido restablecida con éxito! Ya puedes iniciar sesión."
                mensaje.color = "green"

        conn.close()
        page.update()


    return ft.View(
        f"/reset_password/{token}",
        [
            ft.Column(
                [
                    ft.Text("Restablecer Contraseña", size=32, weight="bold"),
                    new_password_input,
                    confirm_password_input,
                    ft.ElevatedButton("Guardar Nueva Contraseña", on_click=handle_reset_password, width=350),
                    mensaje,
                    ft.TextButton("Volver a Inicio de Sesión", on_click=lambda e: page.go("/login"))
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

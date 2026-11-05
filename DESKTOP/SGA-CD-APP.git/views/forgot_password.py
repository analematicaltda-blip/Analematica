import flet as ft
import sqlite3
import secrets
from datetime import datetime, timedelta

def forgot_password_view(page: ft.Page):
    email_input = ft.TextField(label="Ingresa tu correo electrónico", width=350)
    mensaje = ft.Text()

    def handle_send_reset_link(e):
        email = email_input.value.strip()
        if not email:
            mensaje.value = "Por favor, ingresa un correo."
            mensaje.color = "red"
            page.update()
            return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE correo = ?", (email,))
        user = cursor.fetchone()

        if user:
            # Generate a secure token
            token = secrets.token_urlsafe(16)
            # Set expiration time (e.g., 1 hour from now)
            expires = datetime.now() + timedelta(hours=1)

            # Store the token and its expiration in the database
            cursor.execute(
                "UPDATE usuarios SET reset_token = ?, reset_token_expires = ? WHERE id = ?",
                (token, expires.isoformat(), user[0])
            )
            conn.commit()

            # --- Simulate sending an email ---
            # In a real app, you would use an email service here.
            reset_link = f"http://localhost:8550/reset_password/{token}" # Assuming Flet runs on this port
            print("--- SIMULACIÓN DE ENVÍO DE CORREO ---")
            print(f"Para: {email}")
            print(f"Asunto: Recuperación de Contraseña")
            print(f"Haz clic en el siguiente enlace para restablecer tu contraseña:")
            print(reset_link)
            print("------------------------------------")

            mensaje.value = "Si el correo está registrado, recibirás un enlace para restablecer tu contraseña."
            mensaje.color = "green"
        else:
            # Show the same message to prevent user enumeration
            mensaje.value = "Si el correo está registrado, recibirás un enlace para restablecer tu contraseña."
            mensaje.color = "green"

        conn.close()
        page.update()

    return ft.View(
        "/forgot_password",
        [
            ft.Column(
                [
                    ft.Text("Recuperar Contraseña", size=32, weight="bold"),
                    ft.Text("Ingresa tu correo y te enviaremos un enlace para restablecerla."),
                    email_input,
                    ft.ElevatedButton("Enviar Enlace de Recuperación", on_click=handle_send_reset_link, width=350),
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

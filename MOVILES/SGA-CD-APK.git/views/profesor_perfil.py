import flet as ft
import sqlite3

def profesor_perfil(page: ft.Page, user_id: int, tenant_id: int):

    nombre_completo_input = ft.TextField(label="Nombre Completo")
    correo_input = ft.TextField(label="Correo Electrónico")
    telefono_input = ft.TextField(label="Teléfono")

    # Checkboxes for multi-area selection
    cultura_checkbox = ft.Checkbox(label="Área de Cultura", value=False)
    deportes_checkbox = ft.Checkbox(label="Área de Deportes", value=False)

    def cargar_datos():
        conn = sqlite3.connect("formacion.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get basic user info
        cursor.execute("SELECT nombre_completo, correo FROM usuarios WHERE id = ?", (user_id,))
        user_info = cursor.fetchone()
        if user_info:
            nombre_completo_input.value = user_info['nombre_completo']
            correo_input.value = user_info['correo']

        # Get role-specific info (telefono)
        cursor.execute("SELECT telefono FROM profesores WHERE usuario_id = ?", (user_id,))
        profesor_info = cursor.fetchone()
        if profesor_info:
            telefono_input.value = profesor_info['telefono']

        # Get assigned areas
        cursor.execute("SELECT area FROM usuario_areas WHERE usuario_id = ?", (user_id,))
        areas = [row['area'] for row in cursor.fetchall()]
        if "Cultura" in areas:
            cultura_checkbox.value = True
        if "Deportes" in areas:
            deportes_checkbox.value = True

        conn.close()
        page.update()

    def guardar_datos(e):
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        try:
            # Update usuarios and profesores tables
            cursor.execute("UPDATE usuarios SET nombre_completo = ?, correo = ? WHERE id = ?",
                           (nombre_completo_input.value, correo_input.value, user_id))
            cursor.execute("UPDATE profesores SET telefono = ? WHERE usuario_id = ?",
                           (telefono_input.value, user_id))

            # Update areas in the linking table
            # 1. Delete existing associations
            cursor.execute("DELETE FROM usuario_areas WHERE usuario_id = ?", (user_id,))
            # 2. Insert new associations
            if cultura_checkbox.value:
                cursor.execute("INSERT INTO usuario_areas (usuario_id, area) VALUES (?, ?)", (user_id, "Cultura"))
            if deportes_checkbox.value:
                cursor.execute("INSERT INTO usuario_areas (usuario_id, area) VALUES (?, ?)", (user_id, "Deportes"))

            conn.commit()
            page.snack_bar = ft.SnackBar(ft.Text("Perfil actualizado correctamente"), bgcolor="green")
        except Exception as ex:
            conn.rollback()
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"), bgcolor="red")
        finally:
            conn.close()

        page.snack_bar.open = True
        page.update()

    cargar_datos()

    return ft.View(
        "/profesor_perfil",
        [
            ft.AppBar(title=ft.Text("Mi Perfil")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Información Personal y Áreas", size=20, weight="bold"),
                    nombre_completo_input,
                    correo_input,
                    telefono_input,
                    ft.Divider(),
                    ft.Text("Mis Áreas de Especialización", weight="bold"),
                    cultura_checkbox,
                    deportes_checkbox,
                    ft.ElevatedButton("Guardar Cambios", icon=ft.icons.SAVE, on_click=guardar_datos)
                ], scroll=ft.ScrollMode.AUTO)
            )
        ]
    )

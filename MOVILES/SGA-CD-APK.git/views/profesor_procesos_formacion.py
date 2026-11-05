import flet as ft
import sqlite3

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"


def profesor_procesos_formacion(page: ft.Page, tenant_id: int):
    nombre_input = ft.TextField(label="Nombre del Proceso", expand=True)
    tipo_dropdown = ft.Dropdown(
        label="Tipo",
        options=[
            ft.dropdown.Option("Deportivo"),
            ft.dropdown.Option("Cultural")
        ],
        expand=True
    )

    descripcion_input = ft.TextField(label="Descripción", multiline=True, expand=True)

    tabla_procesos = ft.DataTable(columns=[], rows=[], expand=True)

    def guardar_proceso(e):
        nombre = nombre_input.value
        tipo = tipo_dropdown.value
        descripcion = descripcion_input.value

        if not nombre or not tipo:
            page.snack_bar = ft.SnackBar(ft.Text("Todos los campos son obligatorios"))
            page.snack_bar.open = True
            page.update()
            return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        # Table will be created by the setup script
        cursor.execute("""
            INSERT INTO procesos_formacion (inquilino_id, nombre_proceso, tipo_proceso, descripcion)
            VALUES (?, ?, ?, ?)
        """, (tenant_id, nombre, tipo, descripcion))
        conn.commit()
        conn.close()

        nombre_input.value = ""
        tipo_dropdown.value = None
        descripcion_input.value = ""
        cargar_tabla()
        page.update()

    def cargar_tabla():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        # Table will be created by the setup script
        cursor.execute("SELECT nombre_proceso, tipo_proceso, descripcion FROM procesos_formacion WHERE inquilino_id = ?", (tenant_id,))
        datos = cursor.fetchall()
        conn.close()

        tabla_procesos.columns = [
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Tipo")),
            ft.DataColumn(ft.Text("Descripción"))
        ]
        tabla_procesos.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(col))) for col in fila
            ]) for fila in datos
        ]
        page.update()

    # Initial load
    # To prevent errors, we should ensure the table exists before loading.
    # This will be handled by the main app logic calling the db setup first.
    # For now, we can wrap it in a try-except block.
    try:
        cargar_tabla()
    except sqlite3.OperationalError:
        # Table probably doesn't exist yet. It will be created by the setup script.
        print("Tabla 'procesos_formacion' no encontrada. Se creará en la configuración de la BD.")


    return ft.View("/profesor_procesos_formacion", [
        ft.AppBar(title=ft.Text("Gestión de Procesos de Formación"), bgcolor=COLOR1_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[COLOR1_HEX, COLOR2_HEX]
            ),
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=150, height=80),
                ft.Text("Crear un nuevo proceso de formación", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([nombre_input, tipo_dropdown]),
                descripcion_input,
                ft.ElevatedButton("Guardar Proceso", icon=ft.icons.SAVE, on_click=guardar_proceso),
                ft.Divider(),
                ft.Text("Procesos registrados", size=18),
                tabla_procesos
            ], scroll=ft.ScrollMode.AUTO)
        )
    ])

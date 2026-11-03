import flet as ft
import sqlite3

def gestion_areas_view(page: ft.Page, tenant_id: int):

    def get_jefes_disponibles():
        conn = sqlite3.connect("formacion.db")
        # Find users with 'jefe_area' role for the current tenant who are not already assigned to an area
        query = """
            SELECT u.id, u.nombre_completo
            FROM usuarios u
            LEFT JOIN jefes_area ja ON u.id = ja.usuario_id
            WHERE u.rol = 'jefe_area' AND u.inquilino_id = ? AND ja.area_responsabilidad IS NULL
        """
        jefes = conn.execute(query, (tenant_id,)).fetchall()
        conn.close()
        return [ft.dropdown.Option(key=j[0], text=j[1]) for j in jefes]

    def get_jefe_actual(area):
        conn = sqlite3.connect("formacion.db")
        query = """
            SELECT u.nombre_completo
            FROM usuarios u
            JOIN jefes_area ja ON u.id = ja.usuario_id
            WHERE ja.area_responsabilidad = ? AND u.inquilino_id = ?
        """
        jefe = conn.execute(query, (area, tenant_id)).fetchone()
        conn.close()
        return jefe[0] if jefe else "Sin asignar"

    cultura_dropdown = ft.Dropdown(label="Jefe de Área de Cultura", options=get_jefes_disponibles())
    deportes_dropdown = ft.Dropdown(label="Jefe de Área de Deportes", options=get_jefes_disponibles())
    mensaje = ft.Text()

    def asignar_jefe(e, area):
        dropdown = cultura_dropdown if area == 'Cultura' else deportes_dropdown
        nuevo_jefe_id = dropdown.value
        if not nuevo_jefe_id:
            mensaje.value = "Por favor, selecciona un jefe."
            page.update()
            return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        try:
            # Step 1: Unassign any current jefe from this area
            cursor.execute("UPDATE jefes_area SET area_responsabilidad = NULL WHERE area_responsabilidad = ? AND inquilino_id = ?", (area, tenant_id))
            # Step 2: Assign the new jefe
            cursor.execute("UPDATE jefes_area SET area_responsabilidad = ? WHERE usuario_id = ? AND inquilino_id = ?", (area, nuevo_jefe_id, tenant_id))
            conn.commit()
            mensaje.value = f"Jefe de {area} asignado con éxito."
            # Refresh UI
            cultura_jefe_actual.value = f"Jefe Actual: {get_jefe_actual('Cultura')}"
            deportes_jefe_actual.value = f"Jefe Actual: {get_jefe_actual('Deportes')}"
            cultura_dropdown.options = get_jefes_disponibles()
            deportes_dropdown.options = get_jefes_disponibles()
        except Exception as ex:
            mensaje.value = f"Error al asignar jefe: {ex}"
            conn.rollback()
        finally:
            conn.close()
            page.update()

    cultura_jefe_actual = ft.Text(f"Jefe Actual: {get_jefe_actual('Cultura')}")
    deportes_jefe_actual = ft.Text(f"Jefe Actual: {get_jefe_actual('Deportes')}")

    return ft.View(
        "/admin/areas",
        [
            ft.AppBar(title=ft.Text("Gestión de Áreas")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Asignar Jefes de Área", size=22, weight="bold"),
                    ft.Divider(),
                    ft.Text("Área de Cultura", size=18),
                    cultura_jefe_actual,
                    cultura_dropdown,
                    ft.ElevatedButton("Asignar Jefe de Cultura", on_click=lambda e: asignar_jefe(e, 'Cultura')),
                    ft.Divider(height=40),
                    ft.Text("Área de Deportes", size=18),
                    deportes_jefe_actual,
                    deportes_dropdown,
                    ft.ElevatedButton("Asignar Jefe de Deportes", on_click=lambda e: asignar_jefe(e, 'Deportes')),
                    mensaje,
                ])
            )
        ]
    )

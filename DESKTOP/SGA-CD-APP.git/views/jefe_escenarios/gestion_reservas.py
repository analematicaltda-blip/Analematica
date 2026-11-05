import flet as ft
import sqlite3
from datetime import datetime
from utils.notification_service import create_notification

LOGO_PATH = "../../assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

# This view will be stateful to manage the selected part
class GestionReservasView:
    def __init__(self, page: ft.Page, tenant_id: int, escenario_parte_id: int):
        self.page = page
        self.tenant_id = tenant_id
        self.escenario_parte_id = escenario_parte_id

        # --- UI Controls ---
        self.tabla_reservas = ft.DataTable(columns=[], rows=[])
        self.fecha_inicio_input = ft.TextField(label="Fecha/Hora Inicio (YYYY-MM-DD HH:MM)")
        self.fecha_fin_input = ft.TextField(label="Fecha/Hora Fin (YYYY-MM-DD HH:MM)")
        self.proposito_input = ft.TextField(label="Propósito de la Reserva")
        self.usuario_reserva_dropdown = ft.Dropdown(label="Reservado para")

    def cargar_datos_iniciales(self):
        """Load existing reservations and users for the dropdown."""
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        # Load users from the tenant to populate the dropdown
        cursor.execute("SELECT id, nombre_completo FROM usuarios WHERE inquilino_id = ?", (self.tenant_id,))
        self.usuario_reserva_dropdown.options = [ft.dropdown.Option(str(u[0]), u[1]) for u in cursor.fetchall()]

        # Load existing reservations for this specific part
        self.tabla_reservas.columns = [
            ft.DataColumn(ft.Text("Reservado para")),
            ft.DataColumn(ft.Text("Propósito")),
            ft.DataColumn(ft.Text("Desde")),
            ft.DataColumn(ft.Text("Hasta")),
            ft.DataColumn(ft.Text("Estado")),
        ]
        cursor.execute("""
            SELECT u.nombre_completo, r.proposito, r.fecha_inicio, r.fecha_fin, r.estado
            FROM reservas r
            JOIN usuarios u ON r.usuario_id_reserva = u.id
            WHERE r.escenario_parte_id = ? AND r.inquilino_id = ?
            ORDER BY r.fecha_inicio DESC
        """, (self.escenario_parte_id, self.tenant_id))

        self.tabla_reservas.rows = [
            ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row])
            for row in cursor.fetchall()
        ]
        conn.close()
        self.page.update()

    def guardar_nueva_reserva(self, e):
        # --- Conflict Detection Logic ---
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        # Check for overlapping reservations
        cursor.execute("""
            SELECT id FROM reservas
            WHERE escenario_parte_id = ? AND estado = 'Confirmada' AND (
                (fecha_inicio < ? AND fecha_fin > ?) OR -- Overlaps the start
                (fecha_inicio < ? AND fecha_fin > ?) OR -- Overlaps the end
                (fecha_inicio >= ? AND fecha_fin <= ?)   -- Is contained within
            )
        """, (
            self.escenario_parte_id,
            self.fecha_fin_input.value, self.fecha_inicio_input.value,
            self.fecha_fin_input.value, self.fecha_inicio_input.value,
            self.fecha_inicio_input.value, self.fecha_fin_input.value
        ))

        if cursor.fetchone():
            self.page.snack_bar = ft.SnackBar(ft.Text("Conflicto de Horario: Ya existe una reserva en este intervalo de tiempo."), bgcolor="red")
            self.page.snack_bar.open = True
            conn.close()
            self.page.update()
            return

        # --- Save Logic ---
        try:
            usuario_reserva_id = int(self.usuario_reserva_dropdown.value)
            cursor.execute("""
                INSERT INTO reservas (inquilino_id, escenario_parte_id, usuario_id_reserva, proposito, fecha_inicio, fecha_fin)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.tenant_id, self.escenario_parte_id, usuario_reserva_id,
                self.proposito_input.value, self.fecha_inicio_input.value, self.fecha_fin_input.value
            ))
            conn.commit()

            # Send notification to the user for whom the reservation was made
            create_notification(
                tenant_id=self.tenant_id,
                user_id=usuario_reserva_id,
                message=f"Se ha creado una nueva reserva a tu nombre para el {self.fecha_inicio_input.value}.",
                pubsub_instance=self.page.pubsub
            )

            self.page.snack_bar = ft.SnackBar(ft.Text("Reserva creada con éxito."), bgcolor="green")
            self.cargar_datos_iniciales() # Refresh list
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"), bgcolor="red")
        finally:
            conn.close()
            self.page.snack_bar.open = True
            self.page.update()

    def build(self):
        self.cargar_datos_iniciales()
        # The route will need to be dynamic, e.g., /jefe_escenarios/reservas/1
        return ft.View(
            f"/jefe_escenarios/reservas/{self.escenario_parte_id}",
            [
                ft.AppBar(title=ft.Text(f"Reservas para Parte de Escenario ID: {self.escenario_parte_id}"), bgcolor=COLOR2_HEX),
                ft.Container(
                    padding=20, expand=True,
                    content=ft.Column([
                        ft.Text("Crear Nueva Reserva", size=18, weight="bold"),
                        self.usuario_reserva_dropdown,
                        self.proposito_input,
                        self.fecha_inicio_input,
                        self.fecha_fin_input,
                        ft.ElevatedButton("Confirmar Reserva", icon=ft.icons.SAVE, on_click=self.guardar_nueva_reserva),
                        ft.Divider(),
                        ft.Text("Reservas Existentes", size=18, weight="bold"),
                        self.tabla_reservas
                    ])
                )
            ]
        )

def gestion_reservas_view(page: ft.Page, tenant_id: int, escenario_parte_id: int):
    view_instance = GestionReservasView(page, tenant_id, escenario_parte_id)
    return view_instance.build()

import flet as ft
import pandas as pd
import sqlite3
from datetime import datetime

def admin_reporte_asistencia(page: ft.Page, tenant_id: int):

    def get_asistencia_data():
        conn = sqlite3.connect("formacion.db")
        query = """
            SELECT
                u.nombre_completo AS Alumno,
                c.nombre_clase AS Clase,
                p.nombre_completo AS Profesor,
                a.fecha_hora AS Fecha_Asistencia
            FROM asistencias a
            JOIN clases c ON a.clase_id = c.id
            JOIN usuarios u ON a.alumno_id = u.id
            JOIN usuarios p ON c.instructor_id = p.id
            WHERE a.inquilino_id = ?
            ORDER BY a.fecha_hora DESC
        """
        df = pd.read_sql_query(query, conn, params=(tenant_id,))
        conn.close()
        return df

    df = get_asistencia_data()

    def handle_export(e):
        try:
            if df.empty:
                page.snack_bar = ft.SnackBar(ft.Text("No hay datos para exportar."), bgcolor="orange")
            else:
                filename = f"reporte_asistencia_{tenant_id}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                df.to_excel(filename, index=False)
                page.snack_bar = ft.SnackBar(ft.Text(f"Reporte descargado como {filename}"), bgcolor="green")
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al exportar: {ex}"), bgcolor="red")

        page.snack_bar.open = True
        page.update()


    # --- Data Table ---
    columns = [ft.DataColumn(ft.Text(col)) for col in df.columns]
    rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(str(val))) for val in row]) for row in df.itertuples(index=False)]
    data_table = ft.DataTable(columns=columns, rows=rows)

    return ft.View(
        "/admin/reporte_asistencia",
        [
            ft.AppBar(title=ft.Text("Reporte de Asistencia")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Row([
                        ft.Text("Historial de Asistencia", size=22, weight="bold"),
                        ft.ElevatedButton(
                            "Exportar a Excel",
                            icon=ft.icons.DOWNLOAD,
                            on_click=handle_export
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text("Un registro de todas las asistencias marcadas en el sistema."),
                    ft.Divider(),
                    ft.Row([data_table], scroll=ft.ScrollMode.ALWAYS, expand=True)
                ], expand=True)
            )
        ]
    )

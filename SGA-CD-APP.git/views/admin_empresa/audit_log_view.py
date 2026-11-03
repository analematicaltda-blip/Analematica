import flet as ft
import sqlite3
import pandas as pd

def audit_log_view(page: ft.Page, tenant_id: int):

    def get_audit_data():
        conn = sqlite3.connect("formacion.db")
        query = "SELECT timestamp, usuario_id_actor, accion, detalles FROM audit_log WHERE inquilino_id = ? ORDER BY timestamp DESC"
        df = pd.read_sql_query(query, conn, params=(tenant_id,))
        conn.close()
        return df

    df = get_audit_data()

    columns = [ft.DataColumn(ft.Text(col)) for col in df.columns]
    rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(str(val))) for val in row]) for row in df.itertuples(index=False)]

    data_table = ft.DataTable(columns=columns, rows=rows)

    return ft.View(
        "/admin/audit_log",
        [
            ft.AppBar(title=ft.Text("Registro de Auditoría")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Registro de Auditoría", size=22, weight="bold"),
                    ft.Text("Aquí se muestran las acciones importantes realizadas en el sistema."),
                    ft.Divider(),
                    ft.Row([data_table], scroll=ft.ScrollMode.ALWAYS)
                ], scroll=ft.ScrollMode.ALWAYS)
            )
        ]
    )

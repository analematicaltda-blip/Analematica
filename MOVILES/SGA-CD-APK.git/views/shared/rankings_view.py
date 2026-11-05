import flet as ft
import sqlite3
from datetime import datetime, timedelta

def rankings_view(page: ft.Page, tenant_id: int):

    ranking_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Pos.")),
            ft.DataColumn(ft.Text("Alumno")),
            ft.DataColumn(ft.Text("Puntos")),
            ft.DataColumn(ft.Text("Nivel")),
        ],
        rows=[]
    )

    ranking_title = ft.Text("Ranking General (Puntos Totales)", size=18, weight="bold")

    def get_ranking_data(period: str):
        conn = sqlite3.connect("formacion.db")

        if period == "total":
            ranking_title.value = "Ranking General (Puntos Totales)"
            query = """
                SELECT u.nombre_completo, a.puntos_totales, a.nivel
                FROM alumnos a
                JOIN usuarios u ON a.usuario_id = u.id
                WHERE a.inquilino_id = ? AND a.mostrar_en_rankings = 1
                ORDER BY a.puntos_totales DESC
                LIMIT 20
            """
            params = (tenant_id,)

        elif period == "semanal":
            ranking_title.value = "Ranking Semanal"
            one_week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            query = """
                SELECT
                    u.nombre_completo,
                    SUM(pl.puntos_ganados) as puntos_semanales,
                    a.nivel
                FROM gamificacion_puntos_log pl
                JOIN alumnos a ON pl.alumno_id = a.id
                JOIN usuarios u ON a.usuario_id = u.id
                WHERE pl.inquilino_id = ? AND pl.timestamp >= ? AND a.mostrar_en_rankings = 1
                GROUP BY u.nombre_completo, a.nivel
                ORDER BY puntos_semanales DESC
                LIMIT 20
            """
            params = (tenant_id, one_week_ago)

        else:
            conn.close()
            return

        cursor = conn.cursor()
        cursor.execute(query, params)
        data = cursor.fetchall()
        conn.close()

        ranking_table.rows = []
        for i, row in enumerate(data):
            ranking_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(i + 1))),
                    ft.DataCell(ft.Text(row[0])), # Nombre
                    ft.DataCell(ft.Text(str(row[1]))), # Puntos
                    ft.DataCell(ft.Text(str(row[2]))), # Nivel
                ])
            )
        page.update()

    def handle_filter_change(e):
        get_ranking_data(e.control.value)

    filter_dropdown = ft.Dropdown(
        label="Ver Ranking",
        value="total",
        options=[
            ft.dropdown.Option("total", "Puntos Totales"),
            ft.dropdown.Option("semanal", "Puntos de la Semana"),
        ],
        on_change=handle_filter_change
    )

    # Initial load
    get_ranking_data("total")

    return ft.View(
        "/rankings",
        [
            ft.AppBar(title=ft.Text("Tablas de Líderes")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Rankings", size=22, weight="bold"),
                    filter_dropdown,
                    ft.Divider(),
                    ranking_title,
                    ft.Container(content=ranking_table, expand=True)
                ], scroll=ft.ScrollMode.ALWAYS)
            )
        ]
    )

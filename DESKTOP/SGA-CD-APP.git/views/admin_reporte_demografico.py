import flet as ft
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import os

def admin_reporte_demografico(page: ft.Page, tenant_id: int):

    # Ensure the directory for saving plots exists
    os.makedirs("assets/plots", exist_ok=True)
    plot_path = f"assets/plots/demographics_{tenant_id}.png"

    def generate_plot():
        conn = sqlite3.connect("formacion.db")
        query = "SELECT genero, grupo_etario, escolaridad FROM alumnos WHERE inquilino_id = ?"
        df = pd.read_sql_query(query, conn, params=(tenant_id,))
        conn.close()

        if df.empty:
            return None

        # Create a figure with multiple subplots
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        # Plot 1: Gender Distribution
        gender_counts = df['genero'].value_counts()
        axes[0].pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=90)
        axes[0].set_title('Distribución por Género')

        # Plot 2: Age Group Distribution
        age_counts = df['grupo_etario'].value_counts()
        age_counts.plot(kind='bar', ax=axes[1])
        axes[1].set_title('Distribución por Grupo Etario')
        axes[1].set_ylabel('Número de Alumnos')

        # Plot 3: Education Level Distribution
        edu_counts = df['escolaridad'].value_counts()
        edu_counts.plot(kind='barh', ax=axes[2])
        axes[2].set_title('Distribución por Escolaridad')
        axes[2].set_xlabel('Número de Alumnos')

        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()
        return plot_path

    image_src = generate_plot()

    return ft.View(
        "/admin/reporte_demografico",
        [
            ft.AppBar(title=ft.Text("Reporte Demográfico")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Reporte Demográfico de Alumnos", size=22, weight="bold"),
                    ft.Text("Visualización de la distribución de alumnos por diferentes categorías."),
                    ft.Divider(),
                    ft.Image(src=image_src) if image_src else ft.Text("No hay suficientes datos para generar el reporte.")
                ], scroll=ft.ScrollMode.AUTO)
            )
        ]
    )

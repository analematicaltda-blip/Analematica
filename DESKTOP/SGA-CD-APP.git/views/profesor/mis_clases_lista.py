import flet as ft
from utils.api_client import ApiClient

def mis_clases_lista_view(page: ft.Page, user_id: int, tenant_id: int):

    # TODO: La instanciación del ApiClient debería ocurrir una vez y ser pasada por la sesión.
    api_client = ApiClient(
        base_url="http://127.0.0.1:5001",
        tenant_api_key="inquilino_demo_key" # Clave de prueba
    )

    clases_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    def load_clases():
        clases_column.controls.clear()

        # Usar el ApiClient para obtener los datos
        clases = api_client.get_clases_profesor(profesor_id=user_id)

        if clases is None:
            clases_column.controls.append(ft.Text("Error: No se pudieron cargar las clases desde el servidor."))
        elif not clases:
            clases_column.controls.append(ft.Text("No tienes clases asignadas."))
        else:
            for clase in clases:
                clases_column.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(f"Proceso: {clase['nombre_proceso']}", size=16, weight="bold"),
                                ft.Text(f"Clase: {clase['nombre_clase'] or 'N/A'}", style=ft.TextThemeStyle.BODY_LARGE),
                                ft.Text(f"Fecha: {clase['fecha']} a las {clase['hora_inicio']}"),
                                ft.Row(
                                    [
                                        ft.ElevatedButton(
                                            "Ir al Foro",
                                            icon=ft.icons.FORUM,
                                            on_click=lambda e, cid=clase['id']: page.go(f"/clase/{cid}/foro"),
                                            tooltip="Abrir el foro de discusión de la clase"
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.END
                                )
                            ]),
                            padding=15,
                        )
                    )
                )
        page.update()

    load_clases()

    return ft.View(
        "/profesor/mis_clases",
        [
            ft.AppBar(title=ft.Text("Mis Clases"), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Container(
                content=clases_column,
                padding=20,
                expand=True,
            )
        ]
    )

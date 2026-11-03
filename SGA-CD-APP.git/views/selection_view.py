import flet as ft

def selection_view(page: ft.Page):
    """
    Presents the user with the choice to use an API key or a local model.
    """

    def select_api_mode(e):
        page.session.set("mode_selected", "online")
        page.go("/setup/online_mode")

    def select_local_mode(e):
        page.session.set("mode_selected", "offline")
        page.go("/setup/local_model")

    view = ft.View(
        "/selection",
        [
            ft.Column(
                [
                    ft.Text("Bienvenido al Sistema de Gestión Académica", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Para continuar, elija cómo desea utilizar las funciones de Inteligencia Artificial.", size=16),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        text="Modo Online: Usar mi propia Clave de API",
                        icon=ft.icons.CLOUD_SYNC_ROUNDED,
                        on_click=select_api_mode,
                        width=400,
                        height=50,
                    ),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        text="Modo Offline: Descargar un modelo local",
                        icon=ft.icons.COMPUTER_ROUNDED,
                        on_click=select_local_mode,
                        width=400,
                        height=50,
                    ),
                    ft.Container(height=20),
                    ft.Text(
                        "Modo Online requiere una conexión a internet y una clave de API de un proveedor de LLM (ej. OpenAI, Google).",
                        size=12,
                        italic=True,
                        color=ft.colors.GREY_600,
                    ),
                    ft.Text(
                        "Modo Offline descargará un archivo de modelo grande (1.5GB - 3GB) para funcionar sin internet. Requiere un dispositivo potente.",
                        size=12,
                        italic=True,
                        color=ft.colors.GREY_600,
                    ),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return view

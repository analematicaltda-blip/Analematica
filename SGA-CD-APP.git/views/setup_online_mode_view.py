import flet as ft

def setup_online_mode_view(page: ft.Page):
    """
    Allows the user to select which online LLM provider they want to use.
    """

    def select_provider(provider: str):
        page.session.set("selected_provider", provider)
        page.go("/setup/api_key")

    view = ft.View(
        "/setup/online_mode",
        [
            ft.Column(
                [
                    ft.Text("Seleccionar Proveedor Online", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Elige el servicio de Inteligencia Artificial que deseas utilizar."),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        text="OpenAI (GPT-4o, etc.)",
                        icon=ft.icons.FILTER_VINTAGE_ROUNDED,
                        on_click=lambda _: select_provider("openai"),
                        width=400,
                        height=50,
                    ),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        text="Google (Gemini, etc.)",
                        icon=ft.icons.LENS_BLUR_ROUNDED,
                        on_click=lambda _: select_provider("google"),
                        width=400,
                        height=50,
                    ),
                    ft.Container(height=20),
                    ft.TextButton(
                        "Volver",
                        icon=ft.icons.ARROW_BACK_ROUNDED,
                        on_click=lambda _: page.go("/selection")
                    )
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

import flet as ft
from agent.llm_service import initialize_llm, get_llm_status

def setup_api_key_view(page: ft.Page):
    """
    View for the user to enter their API key for the selected provider.
    """
    provider = page.session.get("selected_provider")
    if not provider:
        # Fallback in case the user lands here directly
        page.go("/setup/online_mode")
        return ft.View()

    provider_name = "OpenAI" if provider == "openai" else "Google"

    def show_error_dialog(message: str):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error de Configuración"),
            content=ft.Text(message),
            actions=[ft.TextButton("Entendido", on_click=lambda _: page.close(dlg))],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def save_api_key(e):
        api_key = api_key_field.value
        if not api_key:
            api_key_field.error_text = "La clave no puede estar vacía"
            page.update()
            return

        print(f"--- ⚙️ Guardando clave para el proveedor: {provider} ---")
        config = {
            "llm_preference": provider,
            f"{provider}_api_key": api_key
        }

        initialize_llm(page, config)
        status = get_llm_status()

        if status == "initialized":
            # Guardar la configuración completa para uso futuro
            page.session.set("llm_config", config)
            page.go("/login")
        else:
            show_error_dialog(f"No se pudo inicializar el LLM con la clave proporcionada. Estado: {status}")

    api_key_field = ft.TextField(
        label=f"Clave de API de {provider_name}",
        password=True,
        can_reveal_password=True,
        width=400
    )

    view = ft.View(
        "/setup/api_key",
        [
            ft.Column(
                [
                    ft.Text(f"Configurar {provider_name}", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Por favor, introduce tu clave de API de {provider_name}."),
                    api_key_field,
                    ft.ElevatedButton("Guardar y Continuar", on_click=save_api_key),
                    ft.TextButton(
                        "Volver",
                        icon=ft.icons.ARROW_BACK_ROUNDED,
                        on_click=lambda _: page.go("/setup/online_mode")
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

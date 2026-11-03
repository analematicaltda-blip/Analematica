import flet as ft
from utils.api_client import ApiClient # Asumimos que el ApiClient será creado/pasado

def configuracion_ia_view(page: ft.Page, user_id: int, tenant_id: int):

    # TODO: ApiClient debe ser instanciado una vez y pasado por la sesión de la página
    api_client = ApiClient(base_url="http://127.0.0.1:5001", tenant_api_key="inquilino_demo_key")

    # --- Controles de la UI ---

    llm_provider_dropdown = ft.Dropdown(
        label="Proveedor de LLM Preferido",
        options=[
            ft.dropdown.Option("local", "Modelo Local (Offline, incluido)"),
            ft.dropdown.Option("openai", "OpenAI (Requiere su propia API Key)"),
            ft.dropdown.Option("google", "Google (Requiere su propia API Key)"),
        ],
        # TODO: Cargar el valor guardado actualmente desde la base de datos
        value="local"
    )

    openai_key_field = ft.TextField(
        label="API Key de OpenAI",
        password=True,
        can_reveal_password=True,
        # TODO: Cargar el valor guardado
    )

    google_key_field = ft.TextField(
        label="API Key de Google",
        password=True,
        can_reveal_password=True,
        # TODO: Cargar el valor guardado
    )

    def save_config(e):
        provider = llm_provider_dropdown.value
        openai_key = openai_key_field.value
        google_key = google_key_field.value

        config_data = {
            "llm_preference": provider,
            "openai_api_key": openai_key,
            "google_api_key": google_key
        }

        # TODO: Crear el método `set_llm_config` en ApiClient
        # success = api_client.set_llm_config(config_data)

        # Simulación por ahora:
        success = True

        if success:
            page.snack_bar = ft.SnackBar(ft.Text("¡Configuración guardada con éxito!"), bgcolor="green")
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Error al guardar la configuración."), bgcolor="red")

        page.snack_bar.open = True
        page.update()

    save_button = ft.ElevatedButton("Guardar Configuración", on_click=save_config)

    # TODO: Añadir lógica para cargar la configuración actual al iniciar la vista
    # def load_current_config():
    #     config = api_client.get_llm_config()
    #     if config:
    #         llm_provider_dropdown.value = config.get('llm_preference')
    #         openai_key_field.value = config.get('openai_api_key')
    #         google_key_field.value = config.get('google_api_key')
    #
    # load_current_config()

    return ft.View(
        "/admin/config_ia",
        [
            ft.AppBar(title=ft.Text("Configuración de Inteligencia Artificial"), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Gestión de Proveedores de IA", size=20, weight="bold"),
                        ft.Text(
                            "Aquí puedes elegir si usar el modelo de lenguaje local (incluido, funciona offline) o conectar tu propia cuenta de un proveedor de nube para obtener respuestas potencialmente más potentes (requiere internet).",
                            size=12
                        ),
                        ft.Divider(),
                        llm_provider_dropdown,
                        ft.Text("API Keys de Proveedores en la Nube"),
                        openai_key_field,
                        google_key_field,
                        save_button,
                    ],
                    spacing=15
                ),
                padding=20,
            )
        ]
    )
